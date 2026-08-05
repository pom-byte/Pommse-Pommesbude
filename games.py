import discord
from discord.ext import commands
import random
from database import get_db_connection

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
                    punkte INT DEFAULT 100,
                    highscore INT DEFAULT 0
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS user_fische (
                    user_id BIGINT,
                    fisch_name TEXT,
                    anzahl INT DEFAULT 1,
                    PRIMARY KEY (user_id, fisch_name)
                );
            """)
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            print(f"Fehler bei DB-Init in Games: {e}")

    def get_punkte(self, user_id):
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT punkte FROM user_punkte WHERE user_id = %s;", (user_id,))
            row = cur.fetchone()
            if not row:
                cur.execute("INSERT INTO user_punkte (user_id, punkte, highscore) VALUES (%s, 100, 0) ON CONFLICT (user_id) DO NOTHING;", (user_id,))
                conn.commit()
                punkte = 100
            else:
                punkte = row[0]
            cur.close()
            conn.close()
            return punkte
        except Exception as e:
            print(f"Fehler bei get_punkte: {e}")
            return 100

    def update_punkte(self, user_id, menge):
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT punkte FROM user_punkte WHERE user_id = %s;", (user_id,))
            row = cur.fetchone()
            if not row:
                cur.execute("INSERT INTO user_punkte (user_id, punkte, highscore) VALUES (%s, %s, 0);", (user_id, 100 + menge))
            else:
                if menge > 0:
                    cur.execute("UPDATE user_punkte SET punkte = punkte + %s, highscore = highscore + %s WHERE user_id = %s;", (menge, menge, user_id))
                else:
                    cur.execute("UPDATE user_punkte SET punkte = punkte + %s WHERE user_id = %s;", (menge, user_id))
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            print(f"Fehler bei update_punkte: {e}")

    # --- CASINO & MINISPIELE ---

    @commands.command(name="casino")
    async def casino(self, ctx):
        embed = discord.Embed(
            title="🎰 Willkommen im Knusper-Casino & Spieleparadies!",
            description="Setze deine Knusper-Punkte oder räume ab! Verfügbare Befehle:",
            color=discord.Color.gold()
        )
        embed.add_field(
            name="🔴 Roulette",
            value="Setze auf Farben!\n`!roulette <einsatz> <rot/schwarz/gruen>`",
            inline=False
        )
        embed.add_field(
            name="✂️ Schere, Stein, Papier",
            value="Tritt gegen den Bot an!\n`!ssp <schere/stein/papier> [einsatz]`",
            inline=False
        )
        embed.add_field(
            name="🎲 Würfel-Duell",
            value="Wer würfelt höher?\n`!wuerfel [einsatz]`",
            inline=False
        )
        embed.set_footer(text="Viel Glück! 🍟🎲")
        await ctx.send(embed=embed)

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

        wahl_mapping = {
            "rot": "rot", "red": "rot",
            "schwarz": "schwarz", "black": "schwarz",
            "gruen": "gruen", "green": "gruen", "grün": "gruen"
        }
        
        if wahl not in wahl_mapping:
            await ctx.send("❌ Ungültige Wahl! Nutze: `!roulette <einsatz> <rot/schwarz/gruen>`")
            return

        gewaehlte_farbe = wahl_mapping[wahl]
        ergebnis_zahl = random.randint(0, 36)
        if ergebnis_zahl == 0:
            ergebnis_farbe = "gruen"
        elif ergebnis_zahl % 2 == 0:
            ergebnis_farbe = "schwarz"
        else:
            ergebnis_farbe = "rot"

        embed = discord.Embed(title="🎰 Knusper-Casino Roulette", color=discord.Color.red())
        embed.add_field(name="Gezogene Zahl", value=f"**{ergebnis_zahl}** ({ergebnis_farbe.capitalize()})", inline=False)

        if gewaehlte_farbe == ergebnis_farbe:
            faktor = 14 if ergebnis_farbe == "gruen" else 2
            gewinn = einsatz * faktor
            netto_gewinn = gewinn - einsatz
            self.update_punkte(user_id, netto_gewinn)
            embed.description = f"🎉 **Gewonnen!** Die Kugel landete auf **{ergebnis_farbe.capitalize()}**. Du hast **{gewinn} 🍟** abgeräumt!"
            embed.color = discord.Color.green()
        else:
            self.update_punkte(user_id, -einsatz)
            embed.description = f"😢 **Verloren!** Die Kugel landete auf **{ergebnis_farbe.capitalize()}**. Du hast **{einsatz} 🍟** verloren."
            embed.color = discord.Color.dark_red()

        neuer_stand = self.get_punkte(user_id)
        embed.set_footer(text=f"Neuer Kontostand: {neuer_stand} 🍟")
        await ctx.send(embed=embed)

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
        gewinn_verlust = 0
        ergebnis_text = ""

        if wahl == bot_wahl:
            ergebnis_text = "🤝 **Unentschieden!** Einsatz zurück."
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

        if einsatz > 0 and gewinn_verlust != 0:
            self.update_punkte(user_id, gewinn_verlust)

        embed = discord.Embed(
            title="✂️ Schere, Stein, Papier",
            description=f"Du: {optionen[wahl]} | Bot: {optionen[bot_wahl]}\n\n{ergebnis_text}",
            color=discord.Color.blue()
        )
        if einsatz > 0:
            embed.set_footer(text=f"Einsatz: {einsatz} 🍟 | Neuer Kontostand: {self.get_punkte(user_id)} 🍟")
        
        await ctx.send(embed=embed)

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