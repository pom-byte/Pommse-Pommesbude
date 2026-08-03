import os
from threading import Thread
from flask import Flask
import discord
from discord.ext import commands

# 1. Flask-Server für Render (damit der Web Service aktiv bleibt)
app = Flask('')

@app.route('/')
def home():
    return "Bot ist online und knusprig!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.start()

# 2. Discord Bot Setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Eingeloggt als {bot.user}!")
    # Cogs laden
    try:
        await bot.load_extension("pets")
        print("Cog 'pets' erfolgreich geladen.")
    except Exception as e:
        print(f"Fehler beim Laden von 'pets': {e}")
        
    try:
        await bot.load_extension("inventar")
        print("Cog 'inventar' erfolgreich geladen.")
    except Exception as e:
        print(f"Fehler beim Laden von 'inventar': {e}")

# 3. Starten
if __name__ == "__main__":
    keep_alive()
    TOKEN = os.environ.get("HAUPTBOT_DISCORD_TOKEN")
    bot.run(TOKEN)
