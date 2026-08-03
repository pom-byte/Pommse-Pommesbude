import discord
from discord.ext import commands
import random
from database import get_db_connection

class Pets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.init_db()

    def init_db(self):
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS user_pets (
                    user_id BIGINT PRIMARY KEY,
                    pet_name TEXT,
                    hunger INT DEFAULT 100,
                    level INT DEFAULT 1,
                    accessoires TEXT DEFAULT 'Keine'
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS user_punkte (
                    user_id BIGINT PRIMARY KEY,
                    punkte INT DEFAULT 100
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
            cur.execute("""
                CREATE TABLE IF NOT EXISTS user_inventory (
                    user_id BIGINT,
                    item_name TEXT,
                    wert INT DEFAULT 15
                );
            """)
            cur.execute("""
                ALTER TABLE user_inventory ADD COLUMN IF NOT EXISTS wert INT DEFAULT 15;
            """)
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            print(f"Fehler bei DB-Init in Pets: {e}")

    ZUFALLS_NAMEN = [
        "Knuffi die Fritte", "Sir Crispy Crisp", "Madame Mayo", 
        "Ketchup-King", "Salzige Susi", "Goldgelb der Zerstörer"
    ]

    SHOP_ANGEBOT = {
        "sonnenbrille": {"preis": 500, "typ": "Accessoire", "desc": "Cooler Look für das Pet 🕶️"},
        "ketchup_huetchen": {"preis": 750, "typ": "Accessoire", "desc": "Ein Hütchen aus echtem Ketchup 🍅"},
        "goldene_kruste": {"preis": 2000, "typ": "Upgrade", "desc": "Vergoldet deine Fritte ✨"},
        "spezialfutter": {"preis": 80, "typ": "Futter", "desc": "Gibt deinem Pet direkt +50 Hunger zurück! 🍟"}
    }

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

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT punkte FROM user_punkte WHERE user_id = %s;", (user_id,))
        row = cur.fetchone()
        userpunkte = row[0] if row else 100

        if userpunkte < preis:
            cur.close()
            conn.close()
            await ctx.send(f"❌ Du hast nicht genug Knusper-Punkte! Du brauchst **{preis} 🍟**, hast aber nur **{userpunkte} 🍟**.")
            return

        if item_name == "spezialfutter":
            cur.execute("UPDATE user_punkte SET punkte = punkte - %s WHERE user_id = %s;", (preis, user_id))
            cur.execute("UPDATE user_pets SET hunger = LEAST(100, hunger + 50) WHERE user_id = %s;", (user_id,))
            conn.commit()
            cur.close()
            conn.close()
            await ctx.send(f"🍟 **Lecker!** {ctx.author.mention} hat Spezialfutter gekauft und sein Pet gestärkt!")
            return

        cur.execute("SELECT * FROM user_inventory WHERE user_id = %s AND item_name = %s;", (user_id, item_name))
        if cur.fetchone():
            cur.close()
            conn.close()
            await ctx.send(f"⚠️ Du hast dieses Accessoire bereits gekauft!")
            return

        cur.execute("UPDATE user_punkte SET punkte = punkte - %s WHERE user_id = %s;", (preis, user_id))
        cur.execute("INSERT INTO user_inventory (user_id, item_name, wert) VALUES (%s, %s, %s);", (user_id, item_name, preis))
        cur.execute("UPDATE user_pets SET accessoires = %s WHERE user_id = %s;", (item_name.replace('_', ' ').capitalize(), user_id))

        conn.commit()
        cur.close()
        conn.close()

        await ctx.send(f"🎉 **Erfolgreich gekauft!** {ctx.author.mention} trägt jetzt **{item_name.replace('_', ' ').capitalize()}**!")

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
                    gesamtwert += einzelwert * anzahl
                
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
            await ctx.send("❌ Bitte wähle aus, was du verkaufen möchtest: `!verkaufen fisch` oder `!verkaufen loot`.")
            return

        if gesamtwert <= 0:
            cur.close()
            conn.close()
            await ctx.send(f"❌ In dieser Kategorie (`{kategorie}`) gibt es nichts zu verkaufen!")
            return

        cur.execute("INSERT INTO user_punkte (user_id, punkte) VALUES (%s, %s) ON CONFLICT (user_id) DO UPDATE SET punkte = user_punkte.punkte + %s;", (user_id, gesamtwert, gesamtwert))
        
        conn.commit()
        cur.close()
        conn.close()

        await ctx.send(f"💰 **Erfolgreich verscherbelt!** {ctx.author.mention} hat seinen `{kategorie}` für **{gesamtwert} 🍟** Knusper-Punkte verkauft!")

    @commands.command(name="pet", aliases=["knusperpet"])
    async def pet(self, ctx):
        user_id = ctx.author.id
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT pet_name, hunger, level, accessoires FROM user_pets WHERE user_id = %s;", (user_id,))
        row = cur.fetchone()
        
        if not row:
            zufalls_name = random.choice(self.ZUFALLS_NAMEN)
            cur.execute("INSERT INTO user_pets (user_id, pet_name, hunger, level, accessoires) VALUES (%s, %s, 100, 1, 'Keine') ON CONFLICT (user_id) DO NOTHING;", (user_id, zufalls_name))
            conn.commit()
            pet_name, hunger, level, accessoires = zufalls_name, 100, 1, "Keine"
        else:
            pet_name, hunger, level, accessoires = row[0], row[1], row[2], row[3]
            
        cur.close()
        conn.close()

        embed = discord.Embed(title=f"🐾 Knusper-Pet von {ctx.author.name}", color=discord.Color.orange())
        embed.add_field(name="Name", value=pet_name, inline=False)
        embed.add_field(name="Hunger", value=f"{'🍟' * max(0, (hunger // 20))} ({hunger}/100)", inline=False)
        embed.add_field(name="Level", value=str(level), inline=True)
        embed.add_field(name="Ausstattung", value=accessoires, inline=True)
        embed.set_footer(text="Füttere mit !fuettern oder öffne den Shop mit !menue!")
        
        await ctx.send(embed=embed)

    @commands.command(name="fuettern", aliases=["feed"])
    async def fuettern(self, ctx):
        user_id = ctx.author.id
        futter_kosten = 50

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT punkte FROM user_punkte WHERE user_id = %s;", (user_id,))
        row_eko = cur.fetchone()
        userpunkte = row_eko[0] if row_eko else 100

        if userpunkte < futter_kosten:
            cur.close()
            conn.close()
            await ctx.send(f"❌ Du brauchst **{futter_kosten} 🍟** zum Füttern, hast aber nur **{userpunkte} 🍟**.")
            return

        cur.execute("SELECT hunger FROM user_pets WHERE user_id = %s;", (user_id,))
        row_pet = cur.fetchone()
        hunger = row_pet[0] if row_pet else 100
        nuevo_hunger = min(100, hunger + 25)

        cur.execute("UPDATE user_punkte SET punkte = punkte - %s WHERE user_id = %s;", (futter_kosten, user_id))
        cur.execute("UPDATE user_pets SET hunger = %s WHERE user_id = %s;", (nuevo_hunger, user_id))

        conn.commit()
        cur.close()
        conn.close()

        await ctx.send(f"😋 **Mjam!** Pet für {futter_kosten} 🍟 gefüttert. Neuer Hunger: **{nuevo_hunger}/100**! 🍟✨")

async def setup(bot):
    await bot.add_cog(Pets(bot))