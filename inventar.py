import discord
from discord.ext import commands
import os
import psycopg2

def get_db_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"), sslmode='require')

class Inventar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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

    @commands.command(name="verkaufen", aliases=["pfand", "shop"])
    async def verkaufen(self, ctx, item_id: int = None):
        user_id = ctx.author.id

        if item_id is None:
            await ctx.send("Sag mir schon, *was* du verkaufen willst. Schreib `!verkaufen [Item-ID]`. Nutzen kannst du `!inventar`, um die IDs zu sehen.")
            return

        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Prüfen, ob das Item dem User gehört
            cur.execute(
                "SELECT item_name, item_typ, wert FROM user_inventar WHERE id = %s AND user_id = %s;",
                (item_id, user_id)
            )
            item = cur.fetchone()

            if not item:
                cur.close()
                conn.close()
                await ctx.send("Dieses Item gehört dir nicht (oder es existiert nicht). Netter Versuch.")
                return

            item_name, item_typ, wert = item

            # Item aus dem Inventar löschen
            cur.execute("DELETE FROM user_inventar WHERE id = %s;", (item_id,))
            
            # Hier kannst du später deine Knusperpunkte-Tabelle ansprechen (z.B. Punkte gutschreiben)
            # Aktuell simulieren wir den Verkauf:
            
            conn.commit()
            cur.close()
            conn.close()

            embed = discord.Embed(
                title="💰 Pfandhaus & Recycling",
                description=f"Du hast **{item_name}** erfolgreich entsorgt und **{wert} Knusperpunkte** erhalten!",
                color=discord.Color.green()
            )
            
            if item_typ == "trash":
                kommentar = "Du verkaufst also deinen Müll? Wirtschaftlich fragwürdig, aber wer bin ich, deinen Reichtum zu behindern."
            else:
                kommentar = "Du verkaufst echtes Pet-Gear? Mutig. Oder einfach kurzsichtig."
                
            embed.add_field(name="Pommses Kommentar", value=f"*{kommentar}*", inline=False)
            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send("Fehler beim Verkauf. Das System streikt.")
            print(f"Fehler bei !verkaufen: {e}")

async def setup(bot):
    await bot.add_cog(Inventar(bot))