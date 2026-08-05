import discord
from discord.ext import commands
import random
from database import get_db_connection

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
                    item_typ TEXT,
                    wert INT DEFAULT 0
                );
            """)
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            print(f"Fehler bei DB-Init in Dungeon: {e}")

    @commands.command(name="abenteuer", aliases=["dungeon"])
    async def abenteuer(self, ctx):
        user_id = ctx.author.id
        wurf = random.randint(1, 20)
        
        trash_items = [
            ("Ranzige Socken", 2),
            ("Feuchter Pappbecher", 1),
            ("Halbes Stück trockenes Sauerteigbrot", 3),
            ("Verrostete Büroklammer", 1),
            ("Eine einzelne, laue Pommes vom Vortag", 4)
        ]
        
        common_loot = [
            ("Knuspriger Snack-Rest", 10),
            ("Gefetteter Dungeon-Krümel", 15),
            ("Mini-Ketchup-Tütchen", 20)
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

        if wurf == 1:
            embed.description = (
                "Das war der Boden. Du hast ihn gefunden.\n\n"
                "Pommses Kommentar: *'Ich hätte ja ausgewichen, aber jeder blamiert sich eben auf seine Weise.'*"
            )
            embed.color = discord.Color.dark_red()

        elif 2 <= wurf <= 9:
            item_name, item_wert = random.choice(trash_items)
            self.addItemToDb(user_id, item_name, "trash", item_wert)
            
            embed.description = f"Du hast Müll gefunden: **{item_name}**!"
            embed.color = discord.Color.orange()
            embed.add_field(name="Pommses Kommentar", value="*'Mehr Müll für deine Sammlung. Ich bin tief beeindruckt.'*", inline=False)

        elif 10 <= wurf <= 18:
            item_name, item_wert = random.choice(common_loot)
            self.addItemToDb(user_id, item_name, "loot", item_wert)

            embed.description = f"Du hast den Raum gesäubert und Beute eingesammelt: **{item_name}**!"
            embed.color = discord.Color.blue()
            embed.add_field(name="Pommses Kommentar", value="*'Das war überraschend kompetent. Vergiss nicht zu atmen.'*", inline=False)

        else:
            item_name, item_wert = random.choice(pet_gear_items)
            self.addItemToDb(user_id, item_name, "pet_gear", item_wert)
            
            embed.description = f"🌟 **KRITISCHER ERFOLG!** Du hast episches Pet-Equip gefunden: **{item_name}**!"
            embed.color = discord.Color.gold()
            embed.add_field(name="Pommses Kommentar", value="*'Ich werde das nicht oft sagen: Respekt. Dein Pet sieht fast so furchteinflößend aus wie ich.'*", inline=False)

        embed.set_footer(text="Schau mit !inventar in deinen Rucksack!")
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