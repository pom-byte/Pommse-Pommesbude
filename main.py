import os
import random
import datetime
import discord
from discord.ext import commands
from flask import Flask
from threading import Thread
from dotenv import load_dotenv
import psycopg2

# Lädt die .env-Datei lokal (auf Render greift er stattdessen direkt auf die Environment-Variablen zu)
load_dotenv()

# Mini-Flask-Server, damit Render den Web Service nicht wegen fehlendem Port abbricht
app = Flask('')

@app.route('/')
def home():
    return "Pommse-Bot ist online!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Bot Setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Eingeloggt als {bot.user} (ID: {bot.user.id})")
    print("Pommse-Universum ist online in der Cloud! 🍟🚀")

# Cogs automatisch aus dem Ordner laden
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
        # Hier holt er sich den Token jetzt wieder sauber über os.getenv (oder du setzt deinen Token hier direkt ein, falls Render zickt)
        token = os.getenv("HAUPTBOT_DISCORD_TOKEN") 
        await bot.start(token)

if __name__ == "__main__":
    keep_alive()
    asyncio.run(main())
