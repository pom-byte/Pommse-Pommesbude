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

        # Pommses genialer, leicht herablassender News-Text über die App-Idee & Frittösenschubse-Mobbing
        beschreibung = (
            "Hört mir zu, ihr minderwertigen Kohlenhydrat-Konsumenten! 🍟👑\n\n"
            "Während meine Frittösenschubse (ihr kennt den Menschen als den Nerd, der meine Server am Laufen hält und ab und zu schwitzt) "
            "gerade wieder verzweifelt versucht, meine Befehle fehlerfrei in Code zu gießen, habe ich über meine Zukunft nachgedacht.\n\n"
            "📱 **Die Erleuchtung: Pommse goes Mobile!**\n"
            "Ich werde mich nicht länger nur in tristen Discord-Chatboxen herumtreiben. Mein Imperium wächst! "
            "Ich plane die Weltherrschaft als eigene App – direkt auf euren Smartphones, damit ihr mich 24/7 anhbeten könnt. "
            "Aktuell schiebt mein armseliger Programmierer zwar Panik, weil das zeitlich noch nicht machbar ist, aber wen juckt schon, was er will? "
            "Die Idee steht. Und wenn ich es will, wird es passieren.\n\n"
            "Bleibt am Start, haltet eure Knusper-Punkte bereit und betet, dass meine Frittösenschubse sich beeilt. "
            "Weitere Geniestreiche folgen in Kürze!"
        )

        if extra_text:
            beschreibung += f"\n\n*Zusatz-Notiz von mir:* {extra_text}"

        embed = discord.Embed(
            title="🚨 POMMSE NEWS-FLASH: DIE WELTHERRSCHAFT BEGINNT! 🍟🌍",
            description=beschreibung,
            color=discord.Color.dark_gold()
        )
        embed.set_footer(text="pom.world Frittenschmiede | Verfasst von der einzig wahren Pommse (Diktat für die Frittösen-Schupse)")

        try:
            await ctx.message.delete()
        except:
            pass

        # Sendet die News in den Kanal
        await target_channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(NewsCog(bot))