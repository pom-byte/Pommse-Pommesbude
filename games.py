import discord
from discord.ext import commands
import os
import random
import psycopg2

def get_db_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"), sslmode='require')

class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.init_db()

    def init_db(self):
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS user_punkte (
                    user_id BIGINT PRIMARY KEY,
                    punkte INT DEFAULT 100
                );
            """)
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            print(f"Fehler bei DB-Init in Games: {e}")

    # Hilfsfunktion, um Punkte abzurufen oder zu erstellen
    def get_punkte(self, user_id):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT punkte FROM user_punkte WHERE user_id = %s;", (user_id,))
        row = cur.fetchone()
        if not row:
            cur.execute("INSERT INTO user_punkte (user_id, punkte) VALUES (%s, 100) ON CONFLICT (user_id) DO NOTHING;", (user_id,))
            conn.commit()
            punkte = 100
        else:
            punkte = row[0]
        cur.close()
        conn.close()
        return punkte

    def update_punkte(self, user_id, menge):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO user_punkte (user_id, punkte) VALUES (%s, %s) ON CONFLICT (user_id) DO UPDATE SET punkte = user_punkte.punkte + %s;", (user_id, menge, menge))
        conn.commit()
        cur.close()
        conn.close()

    # --- 1. ROULETTE ---
    @commands.command(name="roulette")
    async def roulette(self, ctx, einsatz: int, wahl: str):
        user_id = ctx.author.id
        wahl = wahl.lower()

        if einsatz <= 0:
            await ctx.send("❌ Der Einsatz muss größer als 0 sein!")
            return

        userpunkte = self.get_punkte(user_id)
        if userpunkte < einsatz:
            await ctx.send(f"❌ Du hast nicht genug Knusper-Punkte! Du hast nur **{userpunkte} 🍟**.")
            return

        gueltige_wahlen = ["rot", "schwarz", "gruen", "schwarz/rot"] # support basic colors
        # Erlauben wir: rot, schwarz, grün (oder 'green', 'red', 'black')
        wahl_mapping = {"rot": "rot", "red": "rot", "schwarz": "schwarz", "black": "schwarz", "gruen": "gruen", "green": "gruen"}
        
        if wahl not in wahl_mapping:
            await ctx.send("❌ Ungültige Wahl! Nutze: `!roulette <einsatz> <rot/schwarz/gruen>`")
            return

        gewaehlte_farbe = wahl_mapping[wahl]

        # Roulette Rad: 0 = Grün (1/37 Chance), 1-18 = Rot, 19-36 = Schwarz (vereinfacht)
        ergebnis_zahl = random.randint(0, 36)
        if ergebnis_zahl == 0:
            ergebnis_farbe = "gruen"
        elif ergebnis_zahl % 2 == 0:
            ergebnis_farbe = "schwarz"
        else:
            ergebnis_farbe = "rot"

        embed = discord.Embed(
            title="🎰 Knusper-Casino Roulette",
            color=discord.Color.red()
        )
        embed.add_field(name="Gezogene Zahl", value=f"**{ergebnis_zahl}** ({ergebnis_farbe.capitalize()})", inline=False)

        if gewaehlte_farbe == ergebnis_farbe:
            # Multiplikator: Grün gibt x14, Rot/Schwarz x2
            faktor = 14 if ergebnis_farbe == "gruen" else 2
            gewinn = einsatz * faktor
            self.update_punkte(user_id, gewinn - einsatz) # Netto-Gewinn draufrechnen
            embed.description = f"🎉 **Gewonnen!** Du hast auf **{gewaehlte_farbe.capitalize()}** gesetzt und **{gewinn} 🍟** abgeräumt!"
            embed.color = discord.Color.green()
        else:
            self.update_punkte(user_id, -einsatz)
            embed.description = f"😢 **Verloren!** Die Kugel landete auf {ergebnis_farbe.capitalize()}. Du hast **{einsatz} 🍟** verloren."
            embed.color = discord.Color.dark_red()

        neuer_stand = self.get_punkte(user_id)
        embed.set_footer(text=f"Neuer Kontostand: {neuer_stand} 🍟")
        await ctx.send(embed=embed)

    # --- 2. SCHERE, STEIN, PAPIER ---
    @commands.command(name="ssp", aliases=["scheresteinpapier"])
    async def ssp(self, ctx, wahl: str, einsatz: int = 0):
        user_id = ctx.author.id
        wahl = wahl.lower()
        optionen = {"schere": "✂️", "stein": "🪨", "papier": "📄"}

        if wahl not in optionen:
            await ctx.send("❌ Ungültige Wahl! Nutze: `!ssp <schere/stein/papier> [einsatz]`")
            return

        if einsatz > 0:
            userpunkte = self.get_punkte(user_id)
            if userpunkte < einsatz:
                await ctx.send(f"❌ Du hast nicht genug Knusper-Punkte für diesen Einsatz ({userpunkte} 🍟 vorhanden).")
                return

        bot_wahl = random.choice(list(optionen.keys()))

        ergebnis_text = ""
        gewinn_verlust = 0

        if wahl == bot_wahl:
            ergebnis_text = "🤝 **Unentschieden!** Niemand gewinnt."
        elif (
            (wahl == "schere" and bot_wahl == "papier") or
            (wahl == "stein" and bot_wahl == "schere") or
            (wahl == "papier" and bot_wahl == "stein")
        ):
            ergebnis_text = f"🎉 **Gewonnen!** Du hast mit {optionen[wahl]} gegen {optionen[bot_wahl]} gewonnen!"
            gewinn_verlust = einsatz
        else:
            ergebnis_text = f"😢 **Verloren!** Der Bot hat mit {optionen[bot_wahl]} gegen {optionen[wahl]} gewonnen."
            gewinn_verlust = -einsatz

        if einsatz > 0:
            self.update_punkte(user_id, gewinn_verlust)

        embed = discord.Embed(
            title="✂️ Schere, Stein, Papier",
            description=f"Du: {optionen[wahl]} | Bot: {optionen[bot_wahl]}\n\n{ergebnis_text}",
            color=discord.Color.blue()
        )
        if einsatz > 0:
            embed.set_footer(text=f"Einsatz: {einsatz} 🍟 | Neuer Kontostand: {self.get_punkte(user_id)} 🍟")
        
        await ctx.send(embed=embed)

    # --- 3. WÜRFEL-SPIEL ---
    @commands.command(name="wuerfel", aliases=["dice", "roll"])
    async def wuerfel(self, ctx, einsatz: int = 0):
        user_id = ctx.author.id

        if einsatz > 0:
            userpunkte = self.get_punkte(user_id)
            if userpunkte < einsatz:
                await ctx.send(f"❌ Du hast nicht genug Knusper-Punkte! Du hast nur **{userpunkte} 🍟**.")
                return

        user_wurf = random.randint(1, 6)
        bot_wurf = random.randint(1, 6)

        embed = discord.Embed(title="🎲 Würfel-Duell", color=discord.Color.gold())
        embed.add_field(name=f"Dein Würfel ({ctx.author.name})", value=f"🎲 **{user_wurf}**", inline=True)
        embed.add_field(name="Bot Würfel", value=f"🎲 **{bot_wurf}**", inline=True)

        if einsatz > 0:
            if user_wurf > bot_wurf:
                self.update_punkte(user_id, einsatz)
                embed.description = f"🎉 **Gewonnen!** Du hast den Bot übertroffen und **{einsatz} 🍟** gewonnen!"
                embed.color = discord.Color.green()
            elif user_wurf < bot_wurf:
                self.update_punkte(user_id, -einsatz)
                embed.description = f"😢 **Verloren!** Der Bot hat höher gewürfelt. Du verlierst **{einsatz} 🍟**."
                embed.color = discord.Color.red()
            else:
                embed.description = f"🤝 **Unentschieden!** Dein Einsatz wurde zurückgegeben."
            embed.set_footer(text=f"Kontostand: {self.get_punkte(user_id)} 🍟")
        else:
            if user_wurf > bot_wurf:
                embed.description = f"🎉 **Du hast gewonnen!** ({user_wurf} vs {bot_wurf})"
            elif user_wurf < bot_wurf:
                embed.description = f"😢 **Der Bot hat gewonnen!** ({user_wurf} vs {bot_wurf})"
            else:
                embed.description = f"🤝 **Unentschieden!** Beide hatten eine {user_wurf}."

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Games(bot))