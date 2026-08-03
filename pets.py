import discord
from discord.ext import commands
import os
import random
import psycopg2

def get_db_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"), sslmode='require')

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
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            print(f"Fehler bei DB-Init in Pets: {e}")

    ZUFALLS_NAMEN = [
        "Knuffi die Fritte", "Sir Crispy Crisp", "Madame Mayo", 
        "Ketchup-King", "Salzige Susi", "Goldgelb der Zerstörer"
    ]

    @commands.command(name="pet", aliases=["knusperpet"])
    async def pet(self, ctx):
        user_id = ctx.author.id
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT pet_name, hunger, level, accessoires FROM user_pets WHERE user_id = %s;", (user_id,))
        row = cur.fetchone()
        
        if not row:
            zufalls_name = random.choice(self.ZUFALLS_NAMEN)
            cur.execute("INSERT INTO user_pets (user_id, pet_name, hunger, level, accessoires) VALUES (%s, %s, 100, 1, 'Keine');", (user_id, zufalls_name))
            conn.commit()
            pet_name, hunger, level, accessoires = zufalls_name, 100, 1, "Keine"
        else:
            pet_name, hunger, level, accessoires = row[0], row[1], row[2], row[3]
            
        cur.close()
        conn.close()

        embed = discord.Embed(
            title=f"🐾 Knusper-Pet von {ctx.author.name}",
            color=discord.Color.orange()
        )
        embed.add_field(name="Name", value=pet_name, inline=False)
        embed.add_field(name="Hunger", value=f"{hunger}/100", inline=True)
        embed.add_field(name="Level", value=str(level), inline=True)
        embed.add_field(name="Ausstattung", value=accessoires, inline=True)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Pets(bot))