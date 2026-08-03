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
        self.hunger_loop.start()

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
            cur.execute("""
                CREATE TABLE IF NOT EXISTS user_punkte (
                    user_id BIGINT PRIMARY KEY,
                    punkte INT DEFAULT 100
                );
            """)
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            print(f"Fehler bei DB-Init in Pets: {e}")

    @tasks.loop(hours=4)
    async def hunger_loop(self):
        try:
            conn = get_db_connection()
            cur = conn.cursor()
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
        "Knuffi die Fritte", "Sir Crispy Crisp", "Madame Mayo", 
        "Ketchup-King", "Salzige Susi", "Goldgelb der Zerstörer"
    ]

    SHOP_ANGEBOT = {
        "sonnenbrille": {"preis": 500, "typ": "Accessoire", "desc": "Cooler Look 🕶️"},
        "ketchup_huetchen": {"preis": 750, "typ": "Accessoire", "desc": "Ketchup-Hütchen 🍅"},
        "goldene_kruste": {"preis": 2000, "typ": "Upgrade", "desc": "Vergoldete Fritte ✨"}
    }

    @commands.command(name="menue", aliases=["shop"])
    async def menue(self, ctx):
        embed = discord.Embed(title="🍟 Fritten-Shop", color=discord.Color.gold())
        for item, daten in self.SHOP_ANGEBOT.items():
            embed.add_field(name=f"{item.replace('_', ' ').capitalize()} ({daten['preis']} 🍟)", value=daten['desc'], inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="pet")
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
            
        cur.close()
        conn.close()

        embed = discord.Embed(title=f"🐾 Knusper-Pet von {ctx.author.name}", color=discord.Color.orange())
        embed.add_field(name="Name", value=pet_name, inline=False)
        embed.add_field(name="Hunger", value=f"{hunger}/100", inline=True)
        embed.add_field(name="Level", value=str(level), inline=True)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Pets(bot))