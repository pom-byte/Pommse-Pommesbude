import discord
from discord.ext import commands

class UpdateCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="update")
    @commands.has_permissions(administrator=True)
    async def update_command(self, ctx, version: str = None, *, beschreibung: str = None):
        if not version:
            await ctx.send("❌ Bitte gib eine Version an! Beispiel: `!update 0.5.1`")
            return

        # -------------------------------------------------------------
        # TRAGE HIER DEINE KANAL-ID EIN (die lange Zahl von deinem Update-Kanal)
        # -------------------------------------------------------------
        UPDATE_CHANNEL_ID = 1533380004443066478  # <--- HIER DEINE ID REIN!
        
        target_channel = self.bot.get_channel(UPDATE_CHANNEL_ID)
        
        # Falls die ID vergessen wurde oder ungültig ist, nimmt er zur Sicherheit den aktuellen Kanal
        if not target_channel:
            target_channel = ctx.channel

        # Fester Standard-Text mit all echten Werten und Features
        if not beschreibung:
            beschreibung = (
                "Aus dem Maschinenraum der Frittenschmiede (pom.world):\n\n"
                "Ein großes Lob an meinen Erschaffer: Der Bot läuft jetzt stabil in der Cloud und das Imperium wächst! 🍟🔥\n\n"
                "🍟 **Was ist neu in diesem Update?**\n"
                "• 🎣 **Angeln:** Die Ruten zappeln wieder, holt euch die dicksten Fische aus dem Frittierfett!\n"
                "• 💰 **Knusper-Punkte & Economy:** Befehle drücken, Knusper-Punkte scheffeln und den Kontostand explodieren lassen!\n"
                "• 🐾 **Pets:** Eure treuen Begleiter sind am Start und passen auf eure Fritten auf!\n"
                "• 🚀 **Cloud-Power:** 24/7 online dank Render und bombensicherem Webserver!"
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

        # Postet das Update jetzt garantiert in den festgelegten Kanal!
        await target_channel.send(embed=embed)
        
        # Falls es in einen anderen Kanal geschickt wurde, kurz Info für dich im Chat
        if target_channel != ctx.channel:
            await ctx.send(f"✅ Update v{version} wurde erfolgreich in den Update-Kanal geschickt!", delete_after=5)

async def setup(bot):
    await bot.add_cog(UpdateCog(bot))