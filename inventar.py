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
            cur.execute("""
                CREATE TABLE IF NOT EXISTS fischeimer (
                    user_id BIGINT,
                    fisch_name TEXT,
                    wert INT DEFAULT 10
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
            
            # 1. D&D-Loot / Müll auslesen
            cur.execute(
                "SELECT id, item_name, item_typ, wert FROM user_inventar WHERE user_id = %s;",
                (user_id,)
            )
            items = cur.fetchall()

            # 2. Fischeimer auslesen
            cur.execute(
                "SELECT fisch_name, wert FROM fischeimer WHERE user_id = %s;",
                (user_id,)
            )
            fische = cur.fetchall()

            cur.close()
            conn.close()
        except Exception as e:
            await ctx.send("Datenbankfehler beim Abrufen des Inventars. Pommse ist am Schlamassel unschuldig.")
            print(f"Fehler bei !inventar: {e}")
            return

        embed = discord.Embed(
            title=f"🎒 Knuspriges Inventar & Eimer von {ctx.author.name}",
            color=discord.Color.gold()
        )

        # Loot / Müll anzeigen
        if items:
            trash_text = ""
            gear_text = ""
            for item_id, name, typ, wert in items:
                if typ == "trash":
                    trash_text += f"• ID **{item_id}**: {name} (*Wert: {wert} 🍟*)\n"
                else:
                    gear_text += f"• ID **{item_id}**: {name} (*Wert: {wert} 🍟*)\n"
            
            if trash_text:
                embed.add_field(name="🗑️ Müll & Andenken (Verkauf mit !pfand <ID>)", value=trash_text, inline=False)
            if gear_text:
                embed.add_field(name="🛡️ Pet-Ausstattung", value=gear_text, inline=False)
        else:
            embed.add_field(name="🗑️ Müll & Loot", value="*Dein Inventar ist leer.*", inline=False)

        # Fischeimer anzeigen
        if fische:
            fisch_text = "\n".join([f"• {f[0]} (*Wert: {f[1]} 🍟*)" for f in fische])
            embed.add_field(name="🐟 Fischeimer (Verkauf mit !verkaufen fisch)", value=fisch_text, inline=False)
        else:
            embed.add_field(name="🐟 Fischeimer", value="*Dein Fischeimer ist leer.*", inline=False)

        embed.set_footer(text="Nutze !pfand <ID> um Müll/Loot einzulösen!")
        await ctx.send(embed=embed)

    @commands.command(name="pfand", aliases=["einloesen", "sellid"])
    async def pfand(self, ctx, item_id: int):
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
                await ctx.send("❌ Dieses Item gehört dir nicht oder die ID existiert nicht. Schau mit `!inventar` nach den richtigen IDs!")
                return

            item_name, item_typ, wert = item

            # Item löschen und Punkte gutschreiben
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
                description=f"Du hast **{item_name}** erfolgreich abgegeben und **{wert} Knusperpunkte** erhalten!",
                color=discord.Color.green()
            )
            
            kommentar = "Du verkaufst also deinen Müll? Wirtschaftlich fragwürdig." if item_typ == "trash" else "Du verkaufst echtes Pet-Gear? Mutig."
            embed.add_field(name="Pommses Kommentar", value=f"*{kommentar}*", inline=False)
            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send("❌ Fehler beim Einlösen. Das System streikt.")
            print(f"Fehler bei !pfand: {e}")

async def setup(bot):
    await bot.add_cog(Inventar(bot))