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
            
            # Tabellen für Pets und Angeln sicherstellen
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
            print(f"Fehler bei DB-Init in Pets/Angeln: {e}")

    ZUFALLS_NAMEN = [
        "Knuffi die Fritte", "Sir Crispy Crisp", "Madame Mayo", 
        "Ketchup-King", "Salzige Susi", "Goldgelb der Zerstörer"
    ]

    FISCHE_LISTE = [
        ("Alte Socke", 40),
        ("Kleine Krabbe", 30),
        ("Frittierter Hering", 15),
        ("Knusper-Lachs", 10),
        ("Garnierte Garnele", 4),
        ("Goldener Knusper-Karpfen", 1)
    ]

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
            
            if last_fed is None:
                last_fed = now
            elif last_fed.tzinfo is None:
                last_fed = last_fed.replace(tzinfo=timezone.utc)
            
            vergangene_stunden = int((now - last_fed).total_seconds() // 3600)
            
            if vergangene_stunden > 0:
                hunger = max(0, old_hunger - (vergangene_stunden * 2))
                cur.execute("""
                    UPDATE user_pets 
                    SET hunger = %s, last_fed = CURRENT_TIMESTAMP 
                    WHERE user_id = %s;
                """, (hunger, user_id))
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
        embed.set_footer(text="Tippe !fuettern um dein Pet zu versorgen oder !angeln für den Fischeimer!")
        
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

    @commands.command(name="angeln", aliases=["fish", "catch"])
    async def angeln(self, ctx):
        user_id = ctx.author.id
        
        # Zufälligen Fisch basierend auf Gewichten auswählen
        namen, gewichte = zip(*self.FISCHE_LISTE)
        geangelt = random.choices(namen, weights=gewichte, k=1)[0]

        conn = get_db_connection()
        cur = conn.cursor()

        # In den Fischeimer (user_fische) abspeichern
        cur.execute("""
            INSERT INTO user_fische (user_id, fisch_name, anzahl) 
            VALUES (%s, %s, 1) 
            ON CONFLICT (user_id, fisch_name) 
            DO UPDATE SET anzahl = user_fische.anzahl + 1;
        """, (user_id, geangelt))

        conn.commit()
        cur.close()
        conn.close()

        fisch_emojis = {
            "Alte Socke": "🧦",
            "Kleine Krabbe": "🦀",
            "Frittierter Hering": "🐟",
            "Knusper-Lachs": "🍣",
            "Garnierte Garnele": "🦐",
            "Goldener Knusper-Karpfen": "✨🐠"
        }
        emoji = fisch_emojis.get(geangelt, "🐟")

        await ctx.send(f"🎣 {ctx.author.mention} wirft die Angel aus und zieht einen Fang an Land: {emoji} **{geangelt}**! *(Schau mit `!inventar` in deinen Eimer)*")

async def setup(bot):
    await bot.add_cog(Pets(bot))