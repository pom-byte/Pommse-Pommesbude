import os
import random
import datetime
import discord
from discord.ext import commands
import psycopg2

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.init_db()

    def get_db_connection(self):
        database_url = os.getenv("DATABASE_URL")
        return psycopg2.connect(database_url, sslmode='require')

    def init_db(self):
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_punkte (
                    user_id BIGINT PRIMARY KEY,
                    punkte INTEGER DEFAULT 0,
                    highscore INTEGER DEFAULT 0
                )
            """)
            cursor.execute("""
                ALTER TABLE user_punkte ADD COLUMN IF NOT EXISTS highscore INTEGER DEFAULT 0;
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_daily (
                    user_id BIGINT PRIMARY KEY,
                    last_daily TEXT
                )
            """)
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Fehler bei DB-Init in Economy: {e}")

    # --- ZENTRALE FUNKTIONEN FÜR PUNKTE & HIGHSCORE ---
    def add_punkte_und_highscore(self, user_id, punkte_delta, highscore_delta):
        """Ändert den Kontostand (kann positiv/negativ sein) und erhöht den Lebenszeit-Highscore."""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO user_punkte (user_id, punkte, highscore) VALUES (%s, 0, 0) ON CONFLICT (user_id) DO NOTHING", 
            (user_id,)
        )
        cursor.execute(
            "UPDATE user_punkte SET punkte = punkte + %s, highscore = highscore + %s WHERE user_id = %s", 
            (punkte_delta, highscore_delta, user_id)
        )
        conn.commit()
        cursor.close()
        conn.close()

    def get_user_daten(self, user_id):
        """Gibt (kontostand, highscore) zurück."""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT punkte, highscore FROM user_punkte WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        if result:
            return result[0], result[1]
        return 0, 0

    # --- AUTOMATISCHER HIGHSCORE IM HINTERGRUND FÜR JEDEN BEFEHL ---
    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        """Wird automatisch im Hintergrund ausgeführt, wenn ein Befehl erfolgreich war (+1 Highscore)."""
        if ctx.author.bot:
            return
        self.add_punkte_und_highscore(ctx.author.id, punkte_delta=0, highscore_delta=1)

    # --- BEFEHLE ---
    @commands.command(name="daily")
    async def daily(self, ctx):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT last_daily FROM user_daily WHERE user_id = %s", (ctx.author.id,))
        result = cursor.fetchone()
        heute = datetime.date.today().isoformat()
        
        if result and result[0] == heute:
            cursor.close()
            conn.close()
            await ctx.send(f"🛑 {ctx.author.mention}, du hast dir deine tägliche Frittier-Ration heute schon abgeholt! Komm morgen wieder.")
            return
            
        self.add_punkte_und_highscore(ctx.author.id, punkte_delta=50, highscore_delta=5)
        cursor.execute("INSERT INTO user_daily (user_id, last_daily) VALUES (%s, %s) ON CONFLICT (user_id) DO UPDATE SET last_daily = %s", (ctx.author.id, heute, heute))
        conn.commit()
        cursor.close()
        conn.close()
        
        kontostand, highscore = self.get_user_daten(ctx.author.id)
        await ctx.send(f"🎉 **Tägliche Fritten-Ration abgeholt!** {ctx.author.mention} bekommt **+50 Knusper-Punkte**!\n*(Neuer Kontostand: {kontostand} 🍟 | Lebenszeit-Highscore: {highscore} ⭐)*")

    @commands.command(name="punkte", aliases=["knusper", "score", "profil"])
    async def punkte_cmd(self, ctx, member: discord.Member = None):
        target = member if member else ctx.author
        kontostand, highscore = self.get_user_daten(target.id)
        
        embed = discord.Embed(
            title=f"🥔 Fritten-Profil von {target.name}",
            color=discord.Color.gold()
        )
        embed.add_field(name="💰 Kontostand", value=f"**{kontostand}** Knusper-Punkte", inline=True)
        embed.add_field(name="🏆 Lebenszeit-Highscore", value=f"**{highscore}** Punkte", inline=True)
        embed.set_footer(text="Der Kontostand ist zum Ausgeben da – der Highscore sinkt nie!")
        await ctx.send(embed=embed)

    @commands.command(name="rangliste", aliases=["leaderboard", "top"])
    async def rangliste(self, ctx):
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, punkte, highscore FROM user_punkte ORDER BY highscore DESC LIMIT 10")
            ergebnisse = cursor.fetchall()
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Datenbankfehler bei Rangliste: {e}")
            return

        if not ergebnisse:
            await ctx.send("🥔 Bisher hat noch niemand das Pommse-Universum bespielt!")
            return

        embed = discord.Embed(
            title="🏆 Pommse-Universum Rangliste (Top Legenden)",
            description="Sortiert nach dem unvergänglichen **Lebenszeit-Highscore** (⭐)!",
            color=discord.Color.orange()
        )
        
        text = ""
        for i, (user_id, kontostand, highscore) in enumerate(ergebnisse, 1):
            user = ctx.guild.get_member(user_id)
            name = user.mention if user else f"User-ID: {user_id}"
            
            medaille = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"#{i}"
            text += f"{medaille} {name} – **{highscore} ⭐** *(Konto: {kontostand} 🍟)*\n"

        embed.add_field(name="Die fleißigsten Frittierer", value=text, inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="give", aliases=["trinkgeld", "schenken"])
    async def give(self, ctx, member: discord.Member, anzahl: int):
        if member == ctx.author:
            await ctx.send("🍟 Du kannst dir doch nicht selbst Punkte schenken, du Schlawiner!")
            return
        if anzahl <= 0:
            await ctx.send("🍟 Du musst schon eine positive Anzahl an Punkten verschenken wollen!")
            return
            
        sender_konto, _ = self.get_user_daten(ctx.author.id)
        if sender_konto < anzahl:
            await ctx.send(f"❌ So viele Punkte hast du gar nicht auf dem Konto! (Aktuell: {sender_konto} 🍟)")
            return
            
        self.add_punkte_und_highscore(ctx.author.id, punkte_delta=-anzahl, highscore_delta=0)
        self.add_punkte_und_highscore(member.id, punkte_delta=anzahl, highscore_delta=0)
        
        await ctx.send(f"💸 {ctx.author.mention} hat **{anzahl} Knusper-Punkte** an {member.mention} rüberschoben! Stabil! 🤝🍟")

    @commands.command(name="cheat", aliases=["adminpunkte", "fabian"])
    @commands.has_permissions(administrator=True)
    async def cheat(self, ctx, anzahl: int, member: discord.Member = None):
        target = member if member else ctx.author
        self.add_punkte_und_highscore(target.id, punkte_delta=anzahl, highscore_delta=anzahl)
        kontostand, highscore = self.get_user_daten(target.id)
        await ctx.send(f"🚨 **ADMIN-CHEAT AKTIVIERT!** {target.mention} hat **{anzahl} Punkte** erhalten!\n*(Konto: {kontostand} 🍟 | Highscore: {highscore} ⭐)* 🛢️✨")

async def setup(bot):
    await bot.add_cog(Economy(bot))