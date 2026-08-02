import discord
from discord.ext import commands
import random
import os
import psycopg2

def get_db_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))

class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- HILFSFUNKTION FÜR PUNKTE ---
    def get_points(self, user_id):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT knusper_punkte FROM user_economy WHERE user_id = %s;", (user_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        return row[0] if row else 0

    def update_points(self, user_id, amount):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO user_economy (user_id, knusper_punkte) 
            VALUES (%s, %s)
            ON CONFLICT (user_id) 
            DO UPDATE SET knusper_punkte = user_economy.knusper_punkte + %s;
        """, (user_id, amount, amount))
        conn.commit()
        cur.close()
        conn.close()

    # --- SCHERE - STEIN - PAPIER ---
    @commands.command(name="ssp")
    async def ssp(self, ctx, wahl: str, einsatz: int = 10):
        """Spiele Schere, Stein, Papier gegen den Bot! Verwendung: !ssp <schere/stein/papier> [einsatz]"""
        wahl = wahl.lower()
        optionen = ["schere", "stein", "papier"]
        
        if wahl not in optionen:
            await ctx.send("❌ Ungültige Wahl! Wähle bitte zwischen: `schere`, `stein` oder `papier`.")
            return

        if einsatz < 1:
            await ctx.send("❌ Der Einsatz muss mindestens 1 Knusper-Punkt betragen!")
            return

        user_punkte = self.get_points(str(ctx.author.id))
        if user_punkte < einsatz:
            await ctx.send(f"❌ Du hast nicht genug Knusper-Punkte! Du besitzt aktuell nur **{user_punkte}** 🍟.")
            return

        bot_wahl = random.choice(optionen)
        
        # Auswertung & Punktewertung (1:1 Quote bei Sieg)
        if wahl == bot_wahl:
            ergebnis = f"🤝 **Unentschieden!** Niemand gewinnt, dein Einsatz von **{einsatz} 🍟** bleibt sicher."
            gewinn = 0
        elif (wahl == "schere" and bot_wahl == "papier") or \
             (wahl == "stein" and bot_wahl == "schere") or \
             (wahl == "papier" and bot_wahl == "stein"):
            ergebnis = f"🎉 **Gewonnen!** Du hast den Bot abgezockt und **+{einsatz}** Knusper-Punkte eingesackt!"
            gewinn = einsatz
        else:
            ergebnis = f"😢 **Verloren!** Der Bot war schneller und hat dir **-{einsatz}** Knusper-Punkte abgeknöpft."
            gewinn = -einsatz

        if gewinn != 0:
            self.update_points(str(ctx.author.id), gewinn)
            
        neuer_stand = self.get_points(str(ctx.author.id))

        embed = discord.Embed(
            title="✂️ Schere - Stein - Papier",
            description=f"Deine Wahl: **{wahl.capitalize()}**\nBot-Wahl: **{bot_wahl.capitalize()}**\n\n{ergebnis}",
            color=discord.Color.green() if gewinn > 0 else (discord.Color.orange() if gewinn == 0 else discord.Color.red())
        )
        embed.set_footer(text=f"Neuer Kontostand: {neuer_stand} Knusper-Punkte 🍟")
        await ctx.send(embed=embed)

    # --- ROULETTE ---
    @commands.command(name="roulette")
    async def roulette(self, ctx, einsatz: int, wahl: str):
        """Spiele Roulette! Wetten auf 'rot', 'schwarz' oder eine Zahl (0-36). Verwendung: !roulette <einsatz> <rot/schwarz/zahl>"""
        wahl = wahl.lower()
        
        if einsatz < 1:
            await ctx.send("❌ Der Einsatz muss mindestens 1 Knusper-Punkt betragen!")
            return

        user_punkte = self.get_points(str(ctx.author.id))
        if user_punkte < einsatz:
            await ctx.send(f"❌ Du hast nicht genug Knusper-Punkte! Du hast nur **{user_punkte}** 🍟.")
            return

        # Gültigkeit der Wahl prüfen
        rote_zahlen = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
        
        is_zahl = False
        try:
            zahl_wahl = int(wahl)
            if 0 <= zahl_wahl <= 36:
                is_zahl = True
            else:
                await ctx.send("❌ Eine Zahl beim Roulette muss zwischen `0` und `36` liegen!")
                return
        except ValueError:
            if wahl not in ["rot", "schwarz"]:
                await ctx.send("❌ Ungültige Wahl! Nutze `rot`, `schwarz` oder eine Zahl von `0` bis `36`.")
                return

        # Drehen des Kessels (0 bis 36)
        ergebnis_zahl = random.randint(0, 36)
        
        # Farbe bestimmen
        if ergebnis_zahl == 0:
            ergebnis_farbe = "gruen"
        elif ergebnis_zahl in rote_zahlen:
            ergebnis_farbe = "rot"
        else:
            ergebnis_farbe = "schwarz"

        gewonnen = False
        gewinn_faktor = 0

        if is_zahl:
            if zahl_wahl == ergebnis_zahl:
                gewonnen = True
                gewinn_faktor = 35  # Direkter Zahlentreffer zahlt 35:1
        else:
            if wahl == ergebnis_farbe:
                gewonnen = True
                gewinn_faktor = 1   # Rot/Schwarz zahlt 1:1

        if gewonnen:
            gewinn = einsatz * gewinn_faktor
            self.update_points(str(ctx.author.id), gewinn)
            ergebnis_text = f"🎉 **Gewinn!** Die Kugel landete auf **{ergebnis_zahl} ({ergebnis_farbe.upper()})**. Du hast **+{gewinn}** Knusper-Punkte abgestaubt!"
        else:
            self.update_points(str(ctx.author.id), -einsatz)
            ergebnis_text = f"💸 **Verloren!** Die Kugel landete auf **{ergebnis_zahl} ({ergebnis_farbe.upper()})**. Leider daneben!"

        neuer_stand = self.get_points(str(ctx.author.id))

        embed = discord.Embed(
            title="🎰 Pommse-Roulette",
            description=f"Dein Einsatz: **{einsatz} 🍟** auf **{wahl.upper()}**\n\n{ergebnis_text}",
            color=discord.Color.green() if gewonnen else discord.Color.red()
        )
        embed.set_footer(text=f"Kontostand: {neuer_stand} Knusper-Punkte 🍟")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Games(bot))