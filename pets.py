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
            cur.execute("INSERT INTO user_pets (user_id, pet_name, hunger, level, accessoires) VALUES (%s, %s, 100, 1, 'Keine') ON CONFLICT (user_id) DO NOTHING;", (user_id, zufalls_name))
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
        embed.add_field(name="Hunger", value=f"{'🍟' * max(0, (hunger // 20))} ({hunger}/100)", inline=False)
        embed.add_field(name="Level", value=str(level), inline=True)
        embed.add_field(name="Ausstattung", value=accessoires, inline=True)
        embed.set_footer(text="Füttere dein Pet mit !fuettern!")
        
        await ctx.send(embed=embed)

    @commands.command(name="fuettern", aliases=["feed"])
    async def fuettern(self, ctx):
        user_id = ctx.author.id
        futter_kosten = 50

        conn = get_db_connection()
        cur = conn.cursor()

        # Punkte prüfen
        cur.execute("SELECT punkte FROM user_punkte WHERE user_id = %s;", (user_id,))
        row_eko = cur.fetchone()
        
        userpunkte = row_eko[0] if row_eko else 100
        if not row_eko:
            cur.execute("INSERT INTO user_punkte (user_id, punkte) VALUES (%s, 100) ON CONFLICT (user_id) DO NOTHING;", (user_id,))

        if userpunkte < futter_kosten:
            cur.close()
            conn.close()
            await ctx.send(f"❌ Du hast nicht genug Knusper-Punkte! Füttern kostet **{futter_kosten} 🍟**, du hast aber nur **{userpunkte} 🍟**.")
            return

        # Pet holen oder erstellen
        cur.execute("SELECT hunger FROM user_pets WHERE user_id = %s;", (user_id,))
        row_pet = cur.fetchone()
        
        if not row_pet:
            zufalls_name = random.choice(self.ZUFALLS_NAMEN)
            cur.execute("INSERT INTO user_pets (user_id, pet_name, hunger, level, accessoires) VALUES (%s, %s, 100, 1, 'Keine');", (user_id, zufalls_name))
            hunger = 100
        else:
            hunger = row_pet[0]

        nuevo_hunger = min(100, hunger + 25)

        # Punkte abziehen und Hunger füllen
        cur.execute("UPDATE user_punkte SET punkte = punkte - %s WHERE user_id = %s;", (futter_kosten, user_id))
        cur.execute("UPDATE user_pets SET hunger = %s WHERE user_id = %s;", (nuevo_hunger, user_id))

        conn.commit()
        cur.close()
        conn.close()

        await ctx.send(f"😋 **Mjam!** {ctx.author.mention} hat sein Pet für {futter_kosten} 🍟 gefüttert. Der Hunger-Status liegt jetzt bei **{nuevo_hunger}/100**! 🍟✨")

async def setup(bot):
    await bot.add_cog(Pets(bot))