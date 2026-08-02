import discord
from discord.ext import commands

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    on_member_join(self, member: discord.Member):
        # -------------------------------------------------------------
        # TRAGE HIER DIE ID DEINES WILLKOMMENS-KANALS EIN
        # -------------------------------------------------------------
        WILLKOMMENS_KANAL_ID = 1533380004443066478  # <--- HIER DEINE KANAL-ID REIN!
        
        channel = self.bot.get_channel(WILLKOMMENS_KANAL_ID)
        if not channel:
            # Falls der Kanal nicht gefunden wird, bricht er ab, damit es keinen Crash gibt
            return

        # Schönes Embed für den neuen User
        embed = discord.Embed(
            title="🍟 Neuer Knusper-Gast an Bord! 🎉",
            description=(
                f"Herzlich willkommen {member.mention} in der **Frittenschmiede (pom.world)**! 🚀\n\n"
                f"Mach es dir gemütlich, schau dich im Casino um und lass die Knusper-Punkte rollen!\n\n"
                f"👉 **Was kannst du tun?**\n"
                f"• Spiel eine Runde `!roulette`, `!ssp` oder `!wuerfel` im Casino.\n"
                f"• Kümmere dich um dein eigenes Knusper-Pet mit `!pet`.\n"
                f"• Schau in den Shop mit `!menue` vorbei.\n\n"
                f"Wir wünschen dir viel Spaß und fröhliches Frittieren! 🍟✨"
            ),
            color=discord.Color.gold()
        )
        
        # Holt das Profilbild des Users (falls vorhanden) als Miniaturansicht
        if member.avatar:
            embed.set_thumbnail(url=member.avatar.url)
        else:
            embed.set_thumbnail(url=member.default_avatar.url)

        embed.set_footer(text=f"Du bist Mitglied #{member.guild.member_count} in unserer Runde!")

        # Sendet die Nachricht in den Kanal
        await channel.send(content=f"Seid gegrüßt! {member.mention} ist eingetroffen!", embed=embed)

async def setup(bot):
    await bot.add_cog(Welcome(bot))