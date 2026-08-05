import discord
from discord.ext import commands
import random
from datetime import datetime, timezone
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
                    accessoires TEXT DEFAULT 'Keine',
                    last_fed TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)
            cur.execute("""
                ALTER TABLE user_pets ADD COLUMN IF NOT EXISTS last_fed TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;
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
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT,
                    item_name TEXT,
                    item_typ TEXT DEFAULT 'trash',
                    wert INT DEFAULT 15
                );
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
            cur.execute("UPDATE user_pets SET hunger = LEAST(100, hunger + 50), last_fed = CURRENT_TIMESTAMP WHERE user_id = %s;", (user_id,))
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
        cur.execute("INSERT INTO user_inventory (user_id, item_name, item_typ, wert) VALUES (%s, %s, %s, %s);", (user_id, item_name, "accessoire", preis))
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
        
        cur.execute("SELECT pet_name, hunger, level, accessoires, last_fed FROM user_pets WHERE user_id = %s;", (user_id,))
        row = cur.fetchone()
        
        now = datetime.now(timezone.utc)

        if not row:
            zufalls_name = random.choice(self.ZUFALLS_NAMEN)
            cur.execute("""
                INSERT INTO user_pets (user_id, pet_name, hunger, level, accessoires, last_fed) 
                VALUES (%s, %s, 100, 1, 'Keine', %s) 
                ON CONFLICT (user_id) DO NOTHING;
            """, (user_id, zufalls_name, now))
            conn.commit()
            pet_name, hunger, level, accessoires = zufalls_name, 100, 1, "Keine"
        else:
            pet_name, old_hunger, level, accessoires, last_fed = row[0], row[1], row[2], row[3], row[4]
            
            if last_fed.tzinfo is None:
                last_fed = last_fed.replace(tzinfo=timezone.utc)
            
            vergangene_stunden = int((now - last_fed).total_seconds() // 3600)
            
            if vergangene_stunden > 0:
                hunger = max(0, old_hunger - (vergangene_stunden * 2))
                cur.execute("""
                    UPDATE user_pets 
                    SET hunger = %s, last_fed = last_fed + make_interval(hours => %s) 
                    WHERE user_id = %s;
                """, (hunger, vergangene_stunden, user_id))
                conn.commit()
            else:
                hunger = old_hunger

        cur.close()
        conn.close()

        if hunger > 75:
            status_text = "Pappsatt & glücklich 🥰"
            kommentar = "*{0} schaut dich mit großen, zufriedenen Kulleraugen an und knuspert leise vor sich hin.*"
        elif hunger > 40:
            status_text = "Mäßig knusprig 🙂"
            kommentar = "*{0} fängt an leicht zu bröseln. Ein kleiner Snack wäre bald mal wieder nett!*"
        elif hunger > 15:
            status_text = "Hat Hunger! 🥺"
            kommentar = "*{0} zieht einen Schmollmund. Der Magen knurrt lauter als die Friteuse!*"
        else:
            status_text = "⚠️ AM VERHUNGERN!"
            kommentar = "*{0} droht zu Staub zu zerfallen! Füttere es sofort mit `!fuettern`, bevor es einknickt!*"

        embed = discord.Embed(title=f"🐾 Knusper-Pet von {ctx.author.name}", color=discord.Color.orange())
        embed.add_field(name="Name", value=f"**{pet_name}**", inline=False)
        embed.add_field(name="Zustand & Hunger", value=f"{'🍟' * max(1, (hunger // 20))} ({hunger}/100)\n*Status: {status_text}*", inline=False)
        embed.add_field(name="Level", value=f"⭐ Stufe {level}", inline=True)
        embed.add_field(name="Glanz & Ausstattung", value=f"✨ {accessoires}", inline=True)
        embed.add_field(name="Pommses Liebeserklärung", value=kommentar.format(pet_name), inline=False)
        embed.set_footer(text="Tippe !fuettern um dein Pet zu versorgen oder !menue für den Shop!")
        
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
        cur.execute("UPDATE user_pets SET hunger = %s, last_fed = CURRENT_TIMESTAMP WHERE user_id = %s;", (nuevo_hunger, user_id))

        conn.commit()
        cur.close()
        conn.close()

        await ctx.send(f"😋 **Mjam!** Pet für {futter_kosten} 🍟 gefüttert. Neuer Hunger: **{nuevo_hunger}/100**! 🍟✨")

    @commands.command(name="inventar", aliases=["inv", "Rucksack", "fischeimer"])
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

        embed.set_footer(text="Nutze !verkaufen loot für Loot oder !verkaufen fisch für den Eimer!")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Pets(bot))