import discord
from discord.ext import commands
import random
import os
import psycopg2

def get_db_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"), sslmode='require')

class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_points(self, user_id):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT punkte FROM user_punkte WHERE user_id = %s;", (int(user_id),))
        row = cur.fetchone()
        cur.close()
        conn.close()
        return row[0] if row else 0

    def update_points(self, user_id, amount):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO user_punkte (user_id, punkte, highscore) 
            VALUES (%s, 0, 0)
            ON CONFLICT (user_id) DO NOTHING;
        """, (int(user_id),))
        cur.execute("""
            UPDATE user_punkte SET punkte = punkte + %s WHERE user_id = %s;
        """, (amount, int(user_id)))
        conn.commit()
        cur.close()
        conn.close()

    @commands.command(name="ssp")
    async def ssp(self, ctx, wahl: str, einsatz: int = 10):
        wahl = wahl.lower()
        optionen = ["schere", "stein", "papier"]
        
        if wahl not in optionen:
            await ctx.send("❌ Ungültige Wahl! Wähle bitte zwischen: `schere`, `stein` oder `papier`.")
            return

        if einsatz < 1:
            await ctx.send("❌ Der Einsatz muss mindestens 1 Knusper-Punkt betragen!")
            return

        user_punkte = self.get_points(ctx.author.id)
        if user_punkte < einsatz:
            await ctx.send(f"❌ Du hast nicht genug Knusper-Punkte! Du besitzt aktuell nur **{user_punkte}** 🍟.")
            return

        bot_wahl = random.choice(optionen)
        
        if wahl == bot_wahl:
            ergebnis = f"🤝 **Unentschieden!** Dein Einsatz von **{einsatz} 🍟** bleibt sicher."
            gewinn = 0
        elif (wahl == "schere" and bot_wahl == "papier") or \
             (wahl == "stein" and bot_wahl == "schere") or \
             (wahl == "papier" and bot_wahl == "stein"):
            ergebnis = f"🎉 **Gewonnen!** Du hast **+{einsatz}** Knusper-Punkte eingesackt!"
            gewinn = einsatz
        else:
            ergebnis = f"😢 **Verloren!** Du hast **-{einsatz}** Knusper-Punkte verloren."
            gewinn = -einsatz

        if gewinn != 0:
            self.update_points(ctx.author.id, gewinn)
            
        neuer_stand = self.get_points(ctx.author.id)

        embed = discord.Embed(
            title="✂️ Schere - Stein - Papier",
            description=f"Deine Wahl: **{wahl.capitalize()}**\nBot-Wahl: **{bot_wahl.capitalize()}**\n\n{ergebnis}",
            color=discord.Color.green() if gewinn > 0 else (discord.Color.orange() if gewinn == 0 else discord.Color.red())
        )
        embed.set_footer(text=f"Neuer Kontostand: {neuer_stand} Knusper-Punkte 🍟")
        await ctx.send(embed=embed)

    @commands.command(name="roulette")
    async def roulette(self, ctx, einsatz: int, wahl: str):
        wahl = wahl.lower()
        
        if einsatz < 1:
            await ctx.send("❌ Der Einsatz muss mindestens 1 Knusper-Punkt betragen!")
            return

        user_punkte = self.get_points(ctx.author.id)
        if user_punkte < einsatz:
            await ctx.send(f"❌ Du hast nicht genug Knusper-Punkte! Du hast nur **{user_punkte}** 🍟.")
            return

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

        ergebnis_zahl = random.randint(0, 36)
        
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
                gewinn_faktor = 35
        else:
            if wahl == ergebnis_farbe:
                gewonnen = True
                gewinn_faktor = 1

        if gewonnen:
            gewinn = einsatz * gewinn_faktor
            self.update_points(ctx.author.id, gewinn)
            ergebnis_text = f"🎉 **Gewinn!** Kugel landete auf **{ergebnis_zahl} ({ergebnis_farbe.upper()})**. **+{gewinn} 🍟**!"
        else:
            self.update_points(ctx.author.id, -einsatz)
            ergebnis_text = f"💸 **Verloren!** Kugel landete auf **{ergebnis_zahl} ({ergebnis_farbe.upper()})**."

        neuer_stand = self.get_points(ctx.author.id)

        embed = discord.Embed(
            title="🎰 Pommse-Roulette",
            description=f"Einsatz: **{einsatz} 🍟** auf **{wahl.upper()}**\n\n{ergebnis_text}",
            color=discord.Color.green() if gewonnen else discord.Color.red()
        )
        embed.set_footer(text=f"Kontostand: {neuer_stand} Knusper-Punkte 🍟")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Games(bot))