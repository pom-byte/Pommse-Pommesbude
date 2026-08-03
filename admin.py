import discord
from discord.ext import commands
from database import get_db_connection

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="cheat", aliases=["adminpunkte"])
    @commands.has_permissions(administrator=True)
    async def cheat(self, ctx, menge: int):
        user_id = ctx.author.id
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO user_punkte (user_id, punkte) VALUES (%s, %s) 
            ON CONFLICT (user_id) DO UPDATE SET punkte = user_punkte.punkte + %s;
        """, (user_id, menge, menge))
        conn.commit()
        cur.close()
        conn.close()
        await ctx.send(f"🚨 **Admin-Cheat aktiviert!** {ctx.author.mention} hat sich **{menge} 🍟** Knusper-Punkte ercheatet!")

async def setup(bot):
    await bot.add_cog(Admin(bot))