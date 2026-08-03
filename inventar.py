import discord
from discord.ext import commands
from database import get_db_connection

class Inventar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.init_db()

    def init_db(self):
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS user_inventar (
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
            print(f"Fehler bei DB-Init in Inventar: {e}")

    @commands.command(name="inventar", aliases=["inv", "tasche"])
    async def inventar(self, ctx):
        user_id = ctx.author.id
        
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                "SELECT id, item_name, item_typ, wert FROM user_inventar WHERE user_id = %s;",
                (user_id,)
            )
            items = cur.fetchall()
            cur.close()
            conn.close()
        except Exception as e:
            await ctx.send("Datenbankfehler beim Abrufen des Inventars. Pommse ist am Schlamassel unschuldig.")
            print(f"Fehler bei !inventar: {e}")
            return

        embed = discord.Embed(
            title=f"🎒 Knuspriges Inventar von {ctx.author.name}",
            color=discord.Color.gold()
        )

        if not items:
            embed.description = "Dein Inventar ist leer. Selbst eine Fritte hat mehr Inhalt."
            embed.add_field(name="Pommses Kommentar", value="*'Vielleicht solltest du mal einen Dungeon betreten statt nur herumzustehen.'*", inline=False)
        else:
            trash_text = ""
            gear_text = ""
            
            for item_id, name, typ, wert in items:
                if typ == "trash":
                    trash_text += f"• ID **{item_id}**: {name} (*Wert: {wert} Knusperpunkte*)\n"
                else:
                    gear_text += f"• ID **{item_id}**: {name} (*Wert: {wert} Knusperpunkte*)\n"
            
            if trash_text:
                embed.add_field(name="🗑️ Müll & Andenken", value=trash_text, inline=False)
            if gear_text:
                embed.add_field(name="🛡️ Pet-Ausstattung", value=gear_text, inline=False)
                
            embed.add_field(name="Pommses Kommentar", value="*'Ein Haufen Zeug. Zumindest glänzt ein Teil davon.'*", inline=False)

        await ctx.send(embed=embed)

    @commands.command(name="verkaufen_id", aliases=["pfand", "sellid"])
    async def verkaufen_id(self, ctx, item_id: int):
        user_id = ctx.author.id

        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            cur.execute(
                "SELECT item_name, item_typ, wert FROM user_inventar WHERE id = %s AND user_id = %s;",
                (item_id, user_id)
            )
            item = cur.fetchone()

            if not item:
                cur.close()
                conn.close()
                await ctx.send("Dieses Item gehört dir nicht (oder die ID existiert nicht). Nutze `!inventar` für die IDs.")
                return

            item_name, item_typ, wert = item

            cur.execute("DELETE FROM user_inventar WHERE id = %s;", (item_id,))
            cur.execute("""
                INSERT INTO user_punkte (user_id, punkte) VALUES (%s, %s) 
                ON CONFLICT (user_id) DO UPDATE SET punkte = user_punkte.punkte + %s;
            """, (user_id, wert, wert))
            
            conn.commit()
            cur.close()
            conn.close()

            embed = discord.Embed(
                title="💰 Pfandhaus & Recycling",
                description=f"Du hast **{item_name}** erfolgreich entsorgt und **{wert} Knusperpunkte** erhalten!",
                color=discord.Color.green()
            )
            
            kommentar = "Du verkaufst also deinen Müll? Wirtschaftlich fragwürdig." if item_typ == "trash" else "Du verkaufst echtes Pet-Gear? Mutig."
            embed.add_field(name="Pommses Kommentar", value=f"*{kommentar}*", inline=False)
            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send("Fehler beim Verkauf. Das System streikt.")
            print(f"Fehler bei !verkaufen_id: {e}")

async def setup(bot):
    await bot.add_cog(Inventar(bot))