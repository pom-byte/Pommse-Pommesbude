import discord
from discord.ext import commands

class UpdateCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="update")
    @commands.has_permissions(administrator=True)
    async def update_command(self, ctx, version: str = None, *, beschreibung: str = None):
        if not version:
            await ctx.send("❌ Bitte gib eine Version an! Beispiel: `!update 0.6.0 Dein Text hier...`")
            return

        # -------------------------------------------------------------
        # TRAGE HIER DEINE ECHTE UPDATE-KANAL-ID EIN
        # -------------------------------------------------------------
        UPDATE_CHANNEL_ID = 1533380004443066478  # <--- HIER DEINE ID REIN!
        
        target_channel = self.bot.get_channel(UPDATE_CHANNEL_ID)
        if not target_channel:
            target_channel = ctx.channel

        # Wenn kein eigener Text übergeben wurde, wird dieser Standard-Text mit den aktuellen Funktionen verwendet
        if not beschreibung:
            beschreibung = (
                "Aus dem Maschinenraum der Frittenschmiede (pom.world):\n\n"
                "Ein großes Lob an unseren Fortschritt: Das Casino und die Features laufen jetzt stabil und reibungslos! 🍟🔥\n\n"
                "🍟 **Was ist neu in diesem Update?**\n"
                "• 🎰 **Casino Roulette:** Setze deine Knusper-Punkte auf Rot, Schwarz oder Grün und räume ab!\n"
                "• ✂️ **Schere, Stein, Papier:** Tritt mit optionalem Einsatz gegen den Bot an!\n"
                "• 🎲 **Würfel-Duell:** Wer wirft die höhere Zahl und gewinnt das Duell?\n"
                "• 🐾 **Pets & Menü:** Füttere deine treuen Begleiter, style sie mit Accessoires und sammle Punkte!\n"
                "• 💰 **Robuste Economy:** Sichere Punkteverwaltung für alle Spieler!"
            )

        embed = discord.Embed(
            title=f"🚨 POMMSE UPDATE {version} IST DA! 🚀",
            description=beschreibung,
            color=discord.Color.gold()
        )
        embed.set_footer(text="pom.world Frittenschmiede | Offizielle Patchnotes 🍟")

        try:
            await ctx.message.delete()
        except:
            pass

        # Postet das Update in den Kanal
        await target_channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(UpdateCog(bot))