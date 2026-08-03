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
                CREATE TABLE IF NOT EXISTS user_inventory (
                    user_id BIGINT,
                    item_name TEXT,
                    wert INT DEFAULT 15
                );
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
            print(f"Fehler bei DB-Init in Inventar: {e}")

    @commands.command(name="inventar", aliases=["inv", "Rucksack"])
    async def inventar(self, ctx):
        user_id = ctx.author.id
        conn = get_db_connection()
        cur = conn.cursor()

        # Loot/Müll auslesen
        cur.execute("SELECT item_name, wert FROM user_inventory WHERE user_id = %s;", (user_id,))
        loot_eintraege = cur.fetchall()

        # Fische auslesen
        cur.execute("SELECT fisch_name, anzahl FROM user_fische WHERE user_id = %s AND anzahl > 0;", (user_id,))
        fische = cur.fetchall()

        cur.close()
        conn.close()

        embed = discord.Embed(
            title=f"🎒 Knuspriges Inventar & Eimer von {ctx.author.name}",
            color=discord.Color.dark_orange()
        )

        # Loot-Bereich
        if loot_eintraege:
            loot_text = ""
            for index, (item_name, wert) in enumerate(loot_eintraege, start=1):
                lesbarer_name = item_name.replace("_", " ").capitalize()
                loot_text += f"• **#{index}**: {lesbarer_name} (*Wert: {wert} 🍟*)\n"
            embed.add_field(name="🗑️ Müll & Andenken", value=loot_text, inline=False)
        else:
            embed.add_field(name="🗑️ Müll & Andenken", value="Dein Inventar ist leer.", inline=False)

        # Fischeimer-Bereich
        if fische:
            fisch_text = ""
            fisch_emojis = {
                "Alte Socke": "🧦",
                "Kleine Krabbe": "🦀",
                "Frittierter Hering": "🐟",
                "Knusper-Lachs": "🍣",
                "Garnierte Garnele": "🦐",
                "Goldener Knusper-Karpfen": "✨🐠"
            }
            for fisch_name, anzahl in fische:
                emoji = fisch_emojis.get(fisch_name, "🐟")
                fisch_text += f"• {emoji} **{fisch_name}**: {anzahl}x\n"
            embed.add_field(name="🪣 Fischeimer", value=fisch_text, inline=False)
        else:
            embed.add_field(name="🪣 Fischeimer", value="Dein Fischeimer ist leer.", inline=False)

        embed.set_footer(text="Nutze !verkaufen loot für Loot oder !verkaufen fisch für den Eimer!")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Inventar(bot))