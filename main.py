import os
from threading import Thread
from flask import Flask
import discord
from discord.ext import commands

# 1. Flask-Server für Render
app = Flask('')

@app.route('/')
def home():
    return "Bot ist online und knusprig!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

# 2. Discord Bot Setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Eingeloggt als {bot.user}!")
    
    # Automatisches Laden aller Cogs im Hauptverzeichnis
    for filename in os.listdir("."):
        if filename.endswith(".py") and filename not in ["main.py", "database.py"]:
            cog_name = filename[:-3]
            # Nur laden, wenn es nicht schon geladen ist
            if cog_name not in bot.extensions:
                try:
                    await bot.load_extension(cog_name)
                    print(f"✅ Cog '{cog_name}' erfolgreich geladen.")
                except Exception as e:
                    print(f"❌ Fehler beim Laden von '{cog_name}': {e}")

# 3. Starten
if __name__ == "__main__":
    keep_alive()
    TOKEN = os.environ.get("HAUPTBOT_DISCORD_TOKEN")
    if not TOKEN:
        print("❌ FEHLER: Kein Token gefunden! Überprüfe die Umgebungsvariable 'HAUPTBOT_DISCORD_TOKEN'.")
    else:
        bot.run(TOKEN)