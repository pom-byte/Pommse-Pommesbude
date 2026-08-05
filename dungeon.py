import discord
from discord.ext import commands
import random
import os
import psycopg2

def get_db_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"), sslmode='require')

class Dungeon(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.init_db()

    def init_db(self):
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS user_inventory (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT,
                    item_name TEXT,
                    item_typ TEXT, -- 'trash' oder 'pet_gear'
                    wert INT DEFAULT 0
                );
            """)
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            print(f"Fehler bei DB-Init in Dungeon: {e}")

    @commands.command(name="abenteuer", aliases=["dungeon", "loot"])
    async def abenteuer(self, ctx):
        user_id = ctx.author.id
        
        # Klassischer d20 Würfelwurf (1 bis 20)
        wurf = random.randint(1, 20)
        
        # Definition von Loot-Pools
        trash_items = [
            ("Ranzige Socken", 2),
            ("Feuchter Pappbecher", 1),
            ("Halbes Stück trockenes Sauerteigbrot", 3),
            ("Verrostete Büroklammer", 1),
            ("Eine einzelne, laue Pommes vom Vortag", 4)
        ]
        
        pet_gear_items = [
            ("Ritterhelm aus Alufolie", 50),
            ("Flammenschwert-Zahnstocher", 75),
            ("Schild aus Toastbrot (leicht angeknuspert)", 60)
        ]

        embed = discord.Embed(
            title="⚔️ Knuspriges Dungeon-Abenteuer",
            color=discord.Color.dark_purple()
        )
        embed.add_field(name=f"Würfelwurf ({ctx.author.name})", value=f"🎲 **{wurf} / 20**", inline=False)

        # Auswertung nach d20-Logik
        if wurf == 1:
            # Episches Versagen
            embed.description = (
                "Das war der Boden. Du hast ihn gefunden.\n\n"
                "Pommses Kommentar: *'Ich hätte ja ausgewichen, aber jeder blamiert sich eben auf seine Weise.'*"
            )
            embed.color = discord.Color.dark_red()

        elif 2 <= wurf <= 9:
            # Mäßiger Erfolg / Müll-Loot
            item_name, item_wert = random.choice(trash_items)
            self.addItemToDb(user_id, item_name, "trash", item_wert)
            
            embed.description = f"Du hast Müll gefunden: **{item_name}**!"
            embed.color = discord.Color.orange()
            
            if "Socken" in item_name:
                kommentar = "Ranzige Socken. Genau das, wovon jede Fritte träumt: Noch mehr Feuchtigkeit."
            elif "Pappbecher" in item_name:
                kommentar = "Ein feuchter Pappbecher. Der natürliche Feind jeglicher Knusprigkeit."
            elif "Sauerteigbrot" in item_name:
                kommentar = "Altes Brot. Wenn uns die Punkte ausgehen, können wir es immerhin noch kauen."
            else:
                kommentar = "Mehr Müll für deine Sammlung. Ich bin tief beeindruckt."
            
            embed.add_field(name="Pommses Kommentar", value=f"*{kommentar}*", inline=False)

        elif 10 <= wurf <= 18:
            # Guter Erfolg
            embed.description = "Du hast den Raum gesäubert und ein paar Knusper-Reste eingesammelt!"
            embed.color = discord.Color.blue()
            embed.add_field(name="Pommses Kommentar", value="*'Das war überraschend kompetent. Vergiss nicht zu atmen.'*", inline=False)

        else:
            # Natürliche 20 (Epischer Pet-Loot)
            item_name, item_wert = random.choice(pet_gear_items)
            self.addItemToDb(user_id, item_name, "pet_gear", item_wert)
            
            embed.description = f"🌟 **KRITISCHER ERFOLG!** Du hast episches Pet-Equip gefunden: **{item_name}**!"
            embed.color = discord.Color.gold()
            embed.add_field(name="Pommses Kommentar", value="*'Ich werde das nicht oft sagen: Respekt. Dein Pet sieht fast so furchteinflößend aus wie ich.'*", inline=False)

        await ctx.send(embed=embed)

    def addItemToDb(self, user_id, item_name, item_typ, wert):
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO user_inventory (user_id, item_name, item_typ, wert) VALUES (%s, %s, %s, %s);",
                (user_id, item_name, item_typ, wert)
            )
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            print(f"Fehler beim Speichern des Loots: {e}")

async def setup(bot):
    await bot.add_cog(Dungeon(bot))