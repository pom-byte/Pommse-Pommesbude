import discord
from discord.ext import commands

class UpdateCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="update")
    @commands.has_permissions(administrator=True)  # Nur Admins dürfen Updates posten
    async def update_command(self, ctx, version: str = None, *, beschreibung: str = "Keine Details angegeben."):
        if not version:
            await ctx.send("❌ Bitte gib eine Versionsnummer an! Beispiel: `!update 0.5.1 Neue Features und Bugfixes`")
            return

        # Hier kannst du die ID deines Willkommens-/Update-Kanals eintragen (ersetze die Zahl mit deiner Kanal-ID)
        # Wenn du ihn einfach in den Kanal schreiben willst, in dem der Befehl ausgeführt wird, nimm ctx.channel
        channel_id = 1533380004443066478  # <--- HIER DEINE KANAL-ID EINTRAGEN (oder ctx.channel nutzen)
        target_channel = self.bot.get_channel(channel_id) or ctx.channel

        # Schönes Embed für das Update erstellen
        embed = discord.Embed(
            title=f"🚀 Pommse-Pommesbude Update v{version}",
            description=beschreibung,
            color=discord.Color.gold()
        )
        embed.set_footer(text="Pommse-Universum Cloud Update 🍟")

        # Nachricht in den Kanal senden
        await target_channel.send(embed=embed)
        
        # Bestätigung im Chat (optional, damit du siehst, dass es geklappt hat)
        if target_channel != ctx.channel:
            await ctx.send(f"✅ Update v{version} wurde erfolgreich in den Kanal gepostet!")

async def setup(bot):
    await bot.add_cog(UpdateCog(bot))