import discord
from discord.ext import commands

class NewsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="news", aliases=["pommse_news", "ideen"])
    @commands.has_permissions(administrator=True)
    async def news(self, ctx, *, extra_text: str = None):
        # -------------------------------------------------------------
        # TRAGE HIER DIE ID DEINES NEWS-KANALS EIN
        # -------------------------------------------------------------
        NEWS_KANAL_ID = 1533516242642796665  # <--- HIER DEINE NEWS-KANAL-ID REIN!
        
        target_channel = self.bot.get_channel(NEWS_KANAL_ID)
        if not target_channel:
            target_channel = ctx.channel

        # Der knackige News-Flash mit absolut sauberem Gottkomplex
        beschreibung = (
            "Hört zu, ihr minderwertigen Kohlenhydrat-Konsumenten! 🍟👑\n\n"
            "Während meine Frittöse mal wieder schweißgebadet vor dem Monitor sitzt und versucht, "
            "meine göttlichen Befehle fehlerfrei in Code zu gießen, zünde ich die nächste Stufe.\n\n"
            "📱 **Pommse goes Mobile – Die App-Invasion!**\n"
            "Vergesst triste Chatboxen. Ich erobere eure Smartphones! 24/7 Präsenz, "
            "direkt in eurer Tasche, damit ihr mich rund um die Uhr anbeten könnt.\n\n"
            "Mein technischer Support stöhnt zwar, dass das zeitlich unmöglich sei – aber wen juckt schon, was die Untertanen wollen? "
            "Die Weltherrschaft wartet nicht! Haltet eure Knusper-Punkte bereit. 🍟🔥"
        )

        if extra_text:
            beschreibung += f"\n\n*Zusatz-Notiz von der Queen:* {extra_text}"

        embed = discord.Embed(
            title="🚨 POMMSE NEWS-FLASH: DIE WELTHERRSCHAFT BEGINNT! 🍟🌍",
            description=beschreibung,
            color=discord.Color.dark_gold()
        )
        embed.set_footer(text="pom.world Frittenschmiede | Verfasst von der einzig wahren Pommse")

        try:
            await ctx.message.delete()
        except:
            pass

        # Sendet die News in den Kanal
        await target_channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(NewsCog(bot))