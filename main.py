import discord
from discord.ext import commands
import os
import asyncio
from flask import Flask
from threading import Thread

# Mini-Flask-Server für Render (damit der Port-Check glücklich ist)
app = Flask("")

@app.route("/")
def home():
    return "Pommse-Bot ist online und frittiert fröhlich vor sich hin! 🍟"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    t = Thread(target=run_flask)
    t.start()

# Ab hier dein normaler Bot-Code
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Eingeloggt als {bot.user} (ID: {bot.user.id})")
    print("Pommse-Universum ist online in der Cloud! 🍟🚀")

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
        await bot.start("HAUPTBOT_DISCORD_TOKEN") # Oder wieder os.getenv, je nachdem wie du es gelöst hast

if __name__ == "__main__":
    keep_alive()  # Startet den Flask-Server im Hintergrund
    asyncio.run(main())
