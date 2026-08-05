import os
import random
import datetime
import discord
from discord.ext import commands
from database import get_db_connection

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.init_db()

    def init_db(self):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # 1. Punktekonto & Highscore
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
            
            # 2. Daily-Tabelle
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_daily (
                    user_id BIGINT PRIMARY KEY,
                    last_daily TEXT
                )
            """)
            
            # 3. Inventar / Shop-Items & Loot
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_inventory (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT,
                    item_name TEXT,
                    item_typ TEXT DEFAULT 'trash',
                    wert INT DEFAULT 15
                );
            """)
            
            # 4. Fischeimer
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_fische (
                    user_id BIGINT,
                    fisch_name TEXT,
                    anzahl INT DEFAULT 1,
                    PRIMARY KEY (user_id, fisch_name)
                );
            """)
            
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Fehler bei DB-Init in Economy: {e}")

    SHOP_ANGEBOT = {
        "sonnenbrille": {"preis": 500, "typ": "Accessoire", "desc": "Cooler Look für das Pet 🕶️"},
        "ketchup_huetchen": {"preis": 750, "typ": "Accessoire", "desc": "Ein Hütchen aus echtem Ketchup 🍅"},
        "goldene_kruste": {"preis": 2000, "typ": "Upgrade", "desc": "Vergoldet deine Fritte ✨"},
        "spezialfutter": {"preis": 80, "typ": "Futter", "desc": "Gibt deinem Pet direkt +50 Hunger zurück! 🍟"}
    }

    def add_punkte_und_highscore(self, user_id, punkte_delta, highscore_delta):
        conn = get_db_connection()
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
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT punkte, highscore FROM user_punkte WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        if result:
            return result[0], result[1]
        return 0, 0

    @commands.command(name="daily")
    async def daily(self, ctx):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT last_daily FROM user_daily WHERE user_id = %s", (ctx.author.id,))
        result = cursor.fetchone()
        heute = datetime.date.today().isoformat()
        
        if result and result[0] == heute:
            cursor.close()
            conn.close()
            await ctx.send(f"🛑 {ctx.author.mention}, du hast dir deine tägliche Frittier-Ration heute schon abgeholt! Komm morgen wieder.")
            return
            
        self.add_punkte_und_highscore(ctx.author.id, punkte_delta=50, highscore_delta=50)
        cursor.execute("INSERT INTO user_daily (user_id, last_daily) VALUES (%s, %s) ON CONFLICT (user_id) DO UPDATE SET last_daily = %s", (ctx.author.id, heute, heute))
        conn.commit()
        cursor.close()
        conn.close()
        
        kontostand, highscore = self.get_user_daten(ctx.author.id)
        await ctx.send(f"🎉 **Tägliche Fritten-Ration abgeholt!** {ctx.author.mention} bekommt **+50 Knusper-Punkte**!\n*(Neuer Kontostand: {kontostand} 🍟 | Lebenszeit-Highscore: {highscore} ⭐)*")

    @commands.command(name="punkte", aliases=["knusper", "score", "profil", "guthaben", "balance"])
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

    @commands.command(name="rangliste", aliases=["leaderboard", "top", "lb"])
    async def rangliste(self, ctx):
        try:
            conn = get_db_connection()
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
            name = f"<@{user_id}>"
            medaille = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"#{i}"
            text += f"{medaille} {name} – **{highscore} ⭐** *(Konto: {kontostand} 🍟)*\n"

        embed.add_field(name="Die fleißigsten Frittierer", value=text, inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="menue", aliases=["shop", "speisekarte"])
    async def menue(self, ctx):
        embed = discord.Embed(
            title="🍟 Pommse' Fritten- & Accessoire-Menü",
            description="Kaufe Upgrades oder verkaufe deinen Loot/Fisch mit `!verkaufen fisch` bzw. `!verkaufen loot`!",
            color=discord.Color.gold()
        )
        for item, daten in self.SHOP_ANGEBOT.items():
            embed.add_field(
                name=f"{item.replace('_', ' ').capitalize()} ({daten['preis']} 🍟)",
                value=f"*{daten['desc']}*",
                inline=False
            )
        embed.set_footer(text="Tippe !kaufen <name> zum Bestellen!")
        await ctx.send(embed=embed)

    @commands.command(name="kaufen")
    async def kaufen(self, ctx, *, item_name: str):
        item_name = item_name.lower().replace(" ", "_")
        if item_name not in self.SHOP_ANGEBOT:
            await ctx.send("❌ Dieses Item steht nicht auf der Speisekarte! Tippe `!menue`.")
            return

        preis = self.SHOP_ANGEBOT[item_name]["preis"]
        user_id = ctx.author.id

        kontostand, _ = self.get_user_daten(user_id)

        if kontostand < preis:
            await ctx.send(f"❌ Du hast nicht genug Knusper-Punkte! Du brauchst **{preis} 🍟**, hast aber nur **{kontostand} 🍟**.")
            return

        conn = get_db_connection()
        cur = conn.cursor()

        # Punkte abziehen
        cur.execute("UPDATE user_punkte SET punkte = punkte - %s WHERE user_id = %s;", (preis, user_id))
        # Ins Inventar legen
        cur.execute("INSERT INTO user_inventory (user_id, item_name, item_typ, wert) VALUES (%s, %s, %s, %s);", (user_id, item_name, "shop_item", preis))
        
        conn.commit()
        cur.close()
        conn.close()

        await ctx.send(f"🎉 **Erfolgreich gekauft!** {ctx.author.mention} hat sich **{item_name.replace('_', ' ').capitalize()}** gegönnt!")

    @commands.command(name="inventar", aliases=["inv", "rucksack", "fischeimer"])
    async def inventar(self, ctx):
        user_id = ctx.author.id
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT item_name, wert FROM user_inventory WHERE user_id = %s;", (user_id,))
        loot_eintraege = cur.fetchall()

        cur.execute("SELECT fisch_name, anzahl FROM user_fische WHERE user_id = %s AND anzahl > 0;", (user_id,))
        fische = cur.fetchall()

        cur.close()
        conn.close()

        embed = discord.Embed(
            title=f"🎒 Knuspriges Inventar & Eimer von {ctx.author.name}",
            color=discord.Color.dark_orange()
        )

        if loot_eintraege:
            loot_text = ""
            for index, (item_name, wert) in enumerate(loot_eintraege, start=1):
                lesbarer_name = item_name.replace("_", " ").capitalize()
                loot_text += f"• **#{index}**: {lesbarer_name} (*Wert: {wert} 🍟*)\n"
            embed.add_field(name="🗑️ Müll, Loot & Ausrüstung", value=loot_text, inline=False)
        else:
            embed.add_field(name="🗑️ Müll, Loot & Ausrüstung", value="Dein Inventar ist leer.", inline=False)

        if fische:
            fisch_text = ""
            fisch_emojis = {
                "Alte Socke": "🧦",
                "Kleine Krabbe": "🦀",
                "Frittierter Hering": "🐟",
                "Knusper-Lachs": "🍣",
                "Garnierte Garnele": "🦐",
                "Goldener Knusper-Karpfen": "✨🐠"
            }
            for fisch_name, anzahl in fische:
                emoji = fisch_emojis.get(fisch_name, "🐟")
                fisch_text += f"• {emoji} **{fisch_name}**: {anzahl}x\n"
            embed.add_field(name="🪣 Fischeimer", value=fisch_text, inline=False)
        else:
            embed.add_field(name="🪣 Fischeimer", value="Dein Fischeimer ist leer.", inline=False)

        embed.set_footer(text="Nutze !verkaufen loot oder !verkaufen fisch, um Dinge zu verscherbeln!")
        await ctx.send(embed=embed)

    @commands.command(name="verkaufen")
    async def verkaufen(self, ctx, kategorie: str):
        user_id = ctx.author.id
        conn = get_db_connection()
        cur = conn.cursor()
        gesamtwert = 0

        kategorie = kategorie.lower()
        if kategorie in ["fish", "fisch", "fischeimer"]:
            cur.execute("SELECT fisch_name, anzahl FROM user_fische WHERE user_id = %s AND anzahl > 0;", (user_id,))
            fische = cur.fetchall()
            
            if fische:
                fisch_werte = {
                    "Alte Socke": 5,
                    "Kleine Krabbe": 15,
                    "Frittierter Hering": 30,
                    "Knusper-Lachs": 60,
                    "Garnierte Garnele": 100,
                    "Goldener Knusper-Karpfen": 300
                }
                for fisch_name, anzahl in fische:
                    einzelwert = fisch_werte.get(fisch_name, 10)
                    gesamtwert += int(einzelwert) * anzahl
                
                cur.execute("DELETE FROM user_fische WHERE user_id = %s;", (user_id,))

        elif kategorie in ["loot", "inventar", "muell"]:
            cur.execute("SELECT SUM(wert) FROM user_inventory WHERE user_id = %s;", (user_id,))
            row = cur.fetchone()
            if row and row[0]:
                gesamtwert = row[0]
                cur.execute("DELETE FROM user_inventory WHERE user_id = %s;", (user_id,))
        else:
            cur.close()
            conn.close()
            await ctx.send("❌ Bitte wähle aus: `!verkaufen fisch` oder `!verkaufen loot`.")
            return

        if gesamtwert <= 0:
            cur.close()
            conn.close()
            await ctx.send(f"❌ In dieser Kategorie (`{kategorie}`) gibt es nichts zu verkaufen!")
            return

        cur.close()
        conn.close()

        # Punkte und Highscore gutschreiben (Verkaufen erhöht den Kontostand, aber Highscore bleibt unberührt oder wächst beim Verdienen - hier nur Kontostand)
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO user_punkte (user_id, punkte) VALUES (%s, %s) ON CONFLICT (user_id) DO UPDATE SET punkte = user_punkte.punkte + %s;", (user_id, gesamtwert, gesamtwert))
        conn.commit()
        cur.close()
        conn.close()

        await ctx.send(f"💰 **Erfolgreich verscherbelt!** {ctx.author.mention} hat seinen `{kategorie}` für **{gesamtwert} 🍟** Knusper-Punkte verkauft!")

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

        self.add_punkte_und_highscore(ctx.author.id, -anzahl, 0)
        self.add_punkte_und_highscore(member.id, anzahl, 0)

        await ctx.send(f"🎁 {ctx.author.mention} hat {member.mention} **{anzahl} 🍟 Knusper-Punkte** geschenkt!")

async def setup(bot):
    await bot.add_cog(Economy(bot))