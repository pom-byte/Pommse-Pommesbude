import os
import asyncio
import discord
from discord.ext import commands
from flask import Flask
from threading import Thread
from dotenv import load_dotenv

load_dotenv()

app = Flask('')

@app.route('/')
def home():
    return "Pommse ist online und frittiert!"

# Bot Setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Eingeloggt als {bot.user} (ID: {bot.user.id})")
    print("Pommse-Universum ist online in der Cloud! 🍟🚀")

async def lade_cogs():
    # Lädt alle Cogs direkt aus dem Hauptverzeichnis (außer der main.py selbst)
    for filename in os.listdir("."):
        if filename.endswith(".py") and filename != "main.py":
            cog_name = filename[:-3]
            try:
                await bot.load_extension(cog_name)
                print(f"Cog erfolgreich geladen: {cog_name}")
            except Exception as e:
                print(f"Fehler beim Laden von Cog {cog_name}: {e}")

@bot.event
async def setup_hook():
    await lade_cogs()

# Startet Flask in einem sicheren Daemon-Thread
def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

if __name__ == "__main__":
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    
    # Bot starten
    token = os.getenv("HAUPTBOT_DISCORD_TOKEN")
    bot.run(token)