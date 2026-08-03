import discord
from discord.ext import commands
import os
import random
import psycopg2

def get_db_connection():
    database_url = os.getenv("DATABASE_URL")
    return psycopg2.connect(database_url, sslmode='require')

class Angeln(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.init_db()

    def init_db(self):
        try:
            conn = get_db_connection()
            cur = conn.cursor()
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
            print(f"Fehler bei DB-Init in Angeln: {e}")

    FANG_TABELLE = [
        ("Alte Socke", "🧦", 5, 25),
        ("Kleine Krabbe", "🦀", 15, 25),
        ("Frittierter Hering", "🐟", 30, 20),
        ("Knusper-Lachs", "🍣", 60, 15),
        ("Garnierte Garnele", "🦐", 100, 10),
        ("Goldener Knusper-Karpfen", "✨🐠", 300, 5)
    ]

    @commands.command(name="angeln", aliases=["fish", "fischen"])
    @commands.cooldown(1, 300, commands.BucketType.user)
    async def angeln(self, ctx):
        fische = [f[0] for f in self.FANG_TABELLE]
        gewichte = [f[3] for f in self.FANG_TABELLE]
        
        gefangener_fisch_name = random.choices(fische, weights=gewichte, k=1)[0]
        fisch_daten = next(f for f in self.FANG_TABELLE if f[0] == gefangener_fisch_name)
        symbol, wert = fisch_daten[1], fisch_daten[2]

        conn = get_db_connection()
        cur = conn.cursor()
        
        # Fisch speichern
        cur.execute("""
            INSERT INTO user_fische (user_id, fisch_name, anzahl)
            VALUES (%s, %s, 1)
            ON CONFLICT (user_id, fisch_name)
            DO UPDATE SET anzahl = user_fische.anzahl + 1;
        """, (ctx.author.id, gefangener_fisch_name))

        # Direkt Knusper-Punkte gutschreiben (Sicherer Direkt-Zugriff auf user_punkte)
        cur.execute("""
            INSERT INTO user_punkte (user_id, punkte) VALUES (%s, %s)
            ON CONFLICT (user_id) DO UPDATE SET punkte = user_punkte.punkte + %s;
        """, (ctx.author.id, wert, wert))

        conn.commit()
        cur.close()
        conn.close()

        embed = discord.Embed(
            title="🎣 Petris Frittier-Heil!",
            description=f"{ctx.author.mention} hat die Angel ausgeworfen und etwas gefangen!",
            color=discord.Color.blue()
        )
        embed.add_field(name="Gefangen:", value=f"{symbol} **{gefangener_fisch_name}**", inline=False)
        embed.add_field(name="Wert:", value=f"💰 **+{wert} Knusper-Punkte**", inline=True)
        embed.set_footer(text="Dein Fang liegt in deinem Eimer (!fischeimer).")

        await ctx.send(embed=embed)

    @angeln.error
    async def angeln_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            minuten = int(error.retry_after // 60)
            sekunden = int(error.retry_after % 60)
            await ctx.send(f"⏳ **Geduld, Anglerkollege!** Die Fische beißen gerade nicht. Warte noch **{minuten}m {sekunden}s**.")

    @commands.command(name="fischeimer", aliases=["fische", "eimer"])
    async def fischeimer(self, ctx):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT fisch_name, anzahl FROM user_fische WHERE user_id = %s AND anzahl > 0;", (ctx.author.id,))
        ergebnisse = cur.fetchall()
        cur.close()
        conn.close()

        if not ergebnisse:
            await ctx.send(f"🪣 {ctx.author.mention}, dein Fischeimer ist noch leer! Tippe `!angeln`.")
            return

        embed = discord.Embed(title=f"🪣 Fischeimer von {ctx.author.name}", color=discord.Color.teal())
        text = ""
        for name, anzahl in ergebnisse:
            symbol = next((f[1] for f in self.FANG_TABELLE if f[0] == name), "🐟")
            text += f"{symbol} **{name}**: {anzahl}x\n"

        embed.description = text
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Angeln(bot))