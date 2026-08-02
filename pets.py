import discord
from discord.ext import commands, tasks
import os
import random
import psycopg2

def get_db_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"), sslmode='require')

class Pets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.init_db()
        self.hunger_loop.start() # Startet den automatischen Hunger-Timer im Hintergrund

    def cog_unload(self):
        self.hunger_loop.cancel()

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
                CREATE TABLE IF NOT EXISTS user_inventory (
                    user_id BIGINT,
                    item_name TEXT,
                    PRIMARY KEY (user_id, item_name)
                );
            """)
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            print(f"Fehler bei DB-Init in Pets: {e}")

    # Automatischer Task: Zieht allen Pets alle 4 Stunden 15 Hunger-Punkte ab
    @tasks.loop(hours=4)
    async def hunger_loop(self):
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            # Zieht 15 Hunger ab, aber minimal bis 0
            cur.execute("UPDATE user_pets SET hunger = GREATEST(0, hunger - 15);")
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            print(f"Fehler im Hunger-Loop: {e}")

    @hunger_loop.before_loop
    async def before_hunger_loop(self):
        await self.bot.wait_until_ready()

    ZUFALLS_NAMEN = [
        "Knuffi die Fritte",
        "Sir Crispy Crisp",
        "Madame Mayo",
        "Ketchup-King",
        "Salzige Susi",
        "Goldgelb der Zerstörer",
        "Frittierte Felicitas",
        "Panierter Paul",
        "Crispy Carl",
        "Dip-Master 3000",
        "Fettige Fratze",
        "Heißes Ölgchen"
    ]

    SHOP_ANGEBOT = {
        "sonnenbrille": {"preis": 500, "typ": "Accessoire", "desc": "Cooler Look für das Pet 🕶️"},
        "ketchup_huetchen": {"preis": 750, "typ": "Accessoire", "desc": "Ein Hütchen aus echtem Ketchup 🍅"},
        "goldene_kruste": {"preis": 2000, "typ": "Upgrade", "desc": "Vergoldet deine Fritte für maximale Flex-Garantie ✨"},
        "extra_dip": {"preis": 300, "typ": "Nahrung", "desc": "Spezielle Joppiesauce für glückliche Pets 🇳🇱"}
    }

    @commands.command(name="menue", aliases=["shop", "speisekarte"])
    async def menue(self, ctx):
        embed = discord.Embed(
            title="🍟 Pommse' Fritten- & Accessoire-Menü",
            description="Kaufe mit deinen Knusper-Punkten (`!kaufen <item>`) stylische Upgrades für dein Pet!",
            color=discord.Color.gold()
        )
        for item, daten in self.SHOP_ANGEBOT.items():
            embed.add_field(
                name=f"{item.replace('_', ' ').capitalize()} ({daten['preis']} 🍟)",
                value=f"*{daten['desc']}*\nTyp: {daten['typ']}",
                inline=False
            )
        embed.set_footer(text="Tippe !kaufen <name> zum Bestellen!")
        await ctx.send(embed=embed)

    @commands.command(name="kaufen")
    async def kaufen(self, ctx, *, item_name: str):
        item_name = item_name.lower().replace(" ", "_")
        if item_name not in self.SHOP_ANGEBOT:
            await ctx.send("❌ Dieses Gericht/Item steht nicht auf unserer Speisekarte! Tippe `!menue`, um das Angebot zu sehen.")
            return

        preis = self.SHOP_ANGEBOT[item_name]["preis"]
        user_id = ctx.author.id
        item_typ = self.SHOP_ANGEBOT[item_name]["typ"]

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT punkte FROM user_punkte WHERE user_id = %s;", (user_id,))
        row = cur.fetchone()
        userpunkte = row[0] if row else 0

        if userpunkte < preis:
            cur.close()
            conn.close()
            await ctx.send(f"❌ Du hast nicht genug Knusper-Punkte! Du brauchst **{preis} 🍟**, hast aber nur **{userpunkte} 🍟**.")
            return

        cur.execute("SELECT * FROM user_inventory WHERE user_id = %s AND item_name = %s;", (user_id, item_name))
        if cur.fetchone():
            cur.close()
            conn.close()
            await ctx.send(f"⚠️ Du hast **{item_name.replace('_', ' ').capitalize()}** bereits gekauft!")
            return

        cur.execute("SELECT user_id FROM user_pets WHERE user_id = %s;", (user_id,))
        if not cur.fetchone():
            zufalls_name = random.choice(self.ZUFALLS_NAMEN)
            cur.execute("""
                INSERT INTO user_pets (user_id, pet_name, hunger, level, accessoires) 
                VALUES (%s, %s, 100, 1, 'Keine');
            """, (user_id, zufalls_name))

        cur.execute("UPDATE user_punkte SET punkte = punkte - %s WHERE user_id = %s;", (preis, user_id))
        cur.execute("INSERT INTO user_inventory (user_id, item_name) VALUES (%s, %s);", (user_id, item_name))
        
        if item_typ in ["Accessoire", "Upgrade"]:
            cur.execute("SELECT item_name FROM user_inventory WHERE user_id = %s;", (user_id,))
            alle_items = cur.fetchall()
            
            gekauft_liste = []
            for (it,) in alle_items:
                if it in self.SHOP_ANGEBOT and self.SHOP_ANGEBOT[it]["typ"] in ["Accessoire", "Upgrade"]:
                    gekauft_liste.append(it.replace("_", " ").capitalize())
            
            neue_acc = ", ".join(gekauft_liste) if gekauft_liste else "Keine"
            cur.execute("UPDATE user_pets SET accessoires = %s WHERE user_id = %s;", (neue_acc, user_id))

        conn.commit()
        cur.close()
        conn.close()

        await ctx.send(f"🎉 **Bestellung erfolgreich!** {ctx.author.mention} hat sich **{item_name.replace('_', ' ').capitalize()}** für {preis} 🍟 gegönnt! Dein Pet trägt es jetzt stolz mit dazu.")

    @commands.command(name="pet", aliases=["knusperpet"])
    async def pet(self, ctx):
        user_id = ctx.author.id
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT pet_name, hunger, level, accessoires FROM user_pets WHERE user_id = %s;", (user_id,))
        row = cur.fetchone()
        
        if not row:
            zufalls_name = random.choice(self.ZUFALLS_NAMEN)
            cur.execute("INSERT INTO user_pets (user_id, pet_name) VALUES (%s, %s) ON CONFLICT (user_id) DO NOTHING;", (user_id, zufalls_name))
            conn.commit()
            pet_name, hunger, level, accessoires = zufalls_name, 100, 1, "Keine"
        else:
            pet_name, hunger, level, accessoires = row[0], row[1], row[2], row[3]
            
            cur.execute("SELECT item_name FROM user_inventory WHERE user_id = %s;", (user_id,))
            alle_items = cur.fetchall()
            gekauft_liste = []
            for (it,) in alle_items:
                if it in self.SHOP_ANGEBOT and self.SHOP_ANGEBOT[it]["typ"] in ["Accessoire", "Upgrade"]:
                    gekauft_liste.append(it.replace("_", " ").capitalize())
            if gekauft_liste:
                accessoires = ", ".join(gekauft_liste)
        
        cur.close()
        conn.close()

        embed = discord.Embed(
            title=f"🐾 Knusper-Pet von {ctx.author.name}",
            description=f"Name: **{pet_name}**\n",
            color=discord.Color.orange()
        )
        embed.add_field(name="Hunger-Status", value=f"{'🍟' * max(0, (hunger // 20))} ({hunger}/100)", inline=False)
        embed.add_field(name="Level", value=f"⭐ {level}", inline=True)
        embed.add_field(name="Ausstattung", value=f"✨ {accessoires}", inline=True)
        embed.set_footer(text="Füttere mit !fuettern oder benenne es mit !petumbenennen um!")
        await ctx.send(embed=embed)

    @commands.command(name="fuettern", aliases=["feed"])
    async def fuettern(self, ctx):
        user_id = ctx.author.id
        futter_kosten = 50

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT punkte FROM user_punkte WHERE user_id = %s;", (user_id,))
        row_eko = cur.fetchone()
        
        if not row_eko:
            cur.execute("INSERT INTO user_punkte (user_id, punkte) VALUES (%s, 100) ON CONFLICT (user_id) DO NOTHING;", (user_id,))
            conn.commit()
            userpunkte = 100
        else:
            userpunkte = row_eko[0]

        if userpunkte < futter_kosten:
            cur.close()
            conn.close()
            await ctx.send(f"❌ Du hast nicht genug Knusper-Punkte! Füttern kostet **{futter_kosten} 🍟**, du hast aber nur **{userpunkte} 🍟**.")
            return

        cur.execute("SELECT hunger FROM user_pets WHERE user_id = %s;", (user_id,))
        row_pet = cur.fetchone()
        
        if not row_pet:
            zufalls_name = random.choice(self.ZUFALLS_NAMEN)
            cur.execute("""
                INSERT INTO user_pets (user_id, pet_name, hunger, level, accessoires) 
                VALUES (%s, %s, 100, 1, 'Keine');
            """, (user_id, zufalls_name))
            hunger = 100
        else:
            hunger = row_pet[0]

        nuevo_hunger = min(100, hunger + 25)

        cur.execute("UPDATE user_punkte SET punkte = punkte - %s WHERE user_id = %s;", (futter_kosten, user_id))
        cur.execute("UPDATE user_pets SET hunger = %s WHERE user_id = %s;", (nuevo_hunger, user_id))

        conn.commit()
        cur.close()
        conn.close()

        await ctx.send(f"😋 **Mjam!** {ctx.author.mention} hat sein Pet für {futter_kosten} 🍟 gefüttert. Der Hunger-Status liegt jetzt bei **{nuevo_hunger}/100**! 🍟✨")

    @commands.command(name="petumbenennen", aliases=["umbenennen"])
    async def petumbenennen(self, ctx, *, neuer_name: str):
        user_id = ctx.author.id
        if len(neuer_name) > 30:
            await ctx.send("❌ Der Name ist zu lang! Max. 30 Zeichen sind erlaubt.")
            return

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT * FROM user_pets WHERE user_id = %s;", (user_id,))
        if not cur.fetchone():
            cur.close()
            conn.close()
            await ctx.send("❌ Du hast noch gar kein Pet! Tippe zuerst `!pet`, um eins zu bekommen.")
            return

        cur.execute("UPDATE user_pets SET pet_name = %s WHERE user_id = %s;", (neuer_name, user_id))
        conn.commit()
        cur.close()
        conn.close()

        await ctx.send(f"✨ **Namensänderung erfolgreich!** Dein Knusper-Pet heißt ab jetzt offiziell **{neuer_name}**! 🍟🐾")

async def setup(bot):
    await bot.add_cog(Pets(bot))