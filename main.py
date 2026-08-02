import os
import asyncio
import discord
from discord.ext import commands
from flask import Flask
from threading import Thread
from dotenv import load_dotenv

load_dotenv()

# Webserver für Render Keep-Alive
app = Flask('')

@app.route('/')
def home():
    return "Pommse ist online und frittiert!"

def run():
    app.run(host='0.0.0.0', port=10000)

Thread(target=run).start()

# Bot Setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Eingeloggt als {bot.user} (ID: {bot.user.id})")
    print("Pommse-Universum ist online in der Cloud! 🍟🚀")

# Funktion zum Laden der Cogs
async def lade_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            cog_name = filename[:-3]
            try:
                await bot.load_extension(f"cogs.{cog_name}")
                print(f"Cog erfolgreich geladen: {cog_name}")
            except Exception as e:
                print(f"Fehler beim Laden von Cog {cog_name}: {e}")

@bot.event
async def setup_hook():
    await lade_cogs()

# Bot starten
token = os.getenv("HAUPTBOT_DISCORD_TOKEN")
bot.run(token)
