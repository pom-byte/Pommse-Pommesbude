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

    def get_punkte(self, user_id):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT punkte FROM user_punkte WHERE user_id = %s;", (user_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        return row[0] if row else 0

    def update_punkte(self, user_id, delta):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO user_punkte (user_id, punkte, highscore) VALUES (%s, 0, 0) ON CONFLICT (user_id) DO NOTHING;", (user_id,))
        cur.execute("UPDATE user_punkte SET punkte = punkte + %s WHERE user_id = %s;", (delta, user_id))
        conn.commit()
        cur.close()
        conn.close()

    # --- 1. STEIN, SCHERE, PAPIER ---
    @commands.command(name="ssp", aliases=["schere", "stein", "papier"])
    async def ssp(self, ctx, wahl: str, einsatz: int):
        wahl = wahl.lower()
        erlaubt = {"stein": "🪨", "schere": "✂️", "papier": "📄"}

        if wahl not in erlaubt:
            await ctx.send("❌ Ungültige Wahl! Nutze: `!ssp <stein/schere/papier> <einsatz>`")
            return
        if einsatz <= 0:
            await ctx.send("❌ Der Einsatz muss größer als 0 sein!")
            return

        user_id = ctx.author.id
        kontostand = self.get_punkte(user_id)

        if kontostand < einsatz:
            await ctx.send(f"❌ Du hast nicht genug Knusper-Punkte! Du hast nur **{kontostand} 🍟**.")
            return

        bot_wahl = random.choice(list(erlaubt.keys()))
        
        if wahl == bot_wahl:
            ergebnis = 0
        elif (wahl == "stein" and bot_wahl == "schere") or \
             (wahl == "schere" and bot_wahl == "papier") or \
             (wahl == "papier" and bot_wahl == "stein"):
            ergebnis = 1
        else:
            ergebnis = -1

        if ergebnis == 1:
            self.update_punkte(user_id, einsatz)
            await ctx.send(f"🎉 Du hast gewonnen! Du wählst {erlaubt[wahl]}, der Bot wählt {erlaubt[bot_wahl]}. Du gewinnst **+{einsatz} 🍟**!")
        elif ergebnis == 0:
            await ctx.send(f"🤝 Unentschieden! Beide wählten {erlaubt[wahl]}. Dein Einsatz von {einsatz} 🍟 bleibt erhalten.")
        else:
            self.update_punkte(user_id, -einsatz)
            await ctx.send(f"😢 Verloren! Du wählst {erlaubt[wahl]}, der Bot wählt {erlaubt[bot_wahl]}. Du verlierst **-{einsatz} 🍟**.")

    # --- 2. ROULETTE ---
    @commands.command(name="roulette")
    async def roulette(self, ctx, wahl: str, einsatz: int):
        wahl = wahl.lower()
        if einsatz <= 0:
            await ctx.send("❌ Der Einsatz muss größer als 0 sein!")
            return

        user_id = ctx.author.id
        kontostand = self.get_punkte(user_id)

        if kontostand < einsatz:
            await ctx.send(f"❌ Du hast nicht genug Knusper-Punkte! Du hast nur **{kontostand} 🍟**.")
            return

        gefallene_zahl = random.randint(0, 10)
        
        if gefallene_zahl == 0:
            farbe = "grün"
        elif gefallene_zahl % 2 == 0:
            farbe = "schwarz"
        else:
            farbe = "rot"

        gewonnen = False
        faktor = 0

        if wahl in ["rot", "schwarz", "grün"]:
            if wahl == farbe:
                gewonnen = True
                faktor = 2 if wahl != "grün" else 10
        elif wahl.isdigit():
            if int(wahl) == gefallene_zahl:
                gewonnen = True
                faktor = 10
        else:
            await ctx.send("❌ Ungültige Wahl! Nutze `!roulette rot <einsatz>`, `!roulette schwarz <einsatz>` oder eine Zahl von 0 bis 10.")
            return

        if gewonnen:
            gewinn = einsatz * (faktor - 1)
            self.update_punkte(user_id, gewinn)
            await ctx.send(f"🎰 Die Kugel landete auf **{gefallene_zahl} ({farbe.upper())}**! Glückwunsch {ctx.author.mention}, du hast gewonnen und kriegst **+{einsatz * faktor} 🍟**!")
        else:
            self.update_punkte(user_id, -einsatz)
            await ctx.send(f"💸 Die Kugel landete auf **{gefallene_zahl} ({farbe.upper())}**. Leider verloren! Du verlierst **-{einsatz} 🍟**.")

    # --- 3. COINFLIP ---
    @commands.command(name="coinflip", aliases=["flip", "muenze"])
    async def coinflip(self, ctx, wahl: str, einsatz: int):
        wahl = wahl.lower()
        if wahl not in ["kopf", "zahl"]:
            await ctx.send("❌ Bitte wähle entweder `kopf` oder `zahl`! (Beispiel: `!coinflip kopf 50`)")
            return
        if einsatz <= 0:
            await ctx.send("❌ Der Einsatz muss größer als 0 sein!")
            return

        user_id = ctx.author.id
        kontostand = self.get_punkte(user_id)

        if kontostand < einsatz:
            await ctx.send(f"❌ Du hast nicht genug Knusper-Punkte! Du hast nur **{kontostand} 🍟**.")
            return

        ergebnis = random.choice(["kopf", "zahl"])

        if wahl == ergebnis:
            self.update_punkte(user_id, einsatz)
            await ctx.send(f"🪙 Die Münze zeigt **{ergebnis.upper()}**! {ctx.author.mention} gewinnt **+{einsatz} 🍟**!")
        else:
            self.update_punkte(user_id, -einsatz)
            await ctx.send(f"🪙 Die Münze zeigt **{ergebnis.upper()}**! Leider daneben, {ctx.author.mention} verliert **-{einsatz} 🍟**.")

async def setup(bot):
    await bot.add_cog(Games(bot))