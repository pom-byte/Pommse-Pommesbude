import discord
from discord.ext import commands
import os
import asyncio

# Bot Setup mit Intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Eingeloggt als {bot.user} (ID: {bot.user.id})")
    print("Pommse-Universum ist online in der Cloud! 🍟🚀")

# Funktion, die alle Cogs aus dem Ordner lädt
async def lade_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            cog_name = filename[:-3]
            try:
                await bot.load_extension(f"cogs.{cog_name}")
                print(f"Cog erfolgreich geladen: {cog_name}")
            except Exception as e:
                print(f"Fehler beim Laden von Cog {cog_name}: {e}")

async def main():
    async with bot:
        await lade_cogs()
        # Token aus den Render-Umgebungsvariablen holen
        await bot.start(os.getenv("DISCORD_TOKEN"))

if __name__ == "__main__":
    asyncio.run(main())
