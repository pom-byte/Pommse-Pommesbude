import discord
from discord.ext import commands
import random

class AutoReply(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignoriere Nachrichten vom Bot selbst, damit es keine Endlosschleife gibt
        if message.author.bot:
            return

        # Den Text komplett in Kleinbuchstaben umwandeln, damit es egal ist, ob groß oder klein geschrieben
        content = message.content.lower()

        # Liste von Trigger-Wörtern und den passenden, frechen Pommse-Antworten
        # Du kannst hier jederzeit neue Wörter oder Sprüche hinzufügen!
        
        if any(word in content for word in ["pommes", "fritte", "fritten", "fritteuse"]):
            antworten = [
                "Hat hier gerade jemand meinen heiligen Namen genannt?! 🍟 Kniet nieder vor der Knusprigkeit!",
                "Wer wagt es, mich ohne eine Portion Mayo im Mund zu erwähnen? Unfassbar. 🙄🍟",
                "Fritten an die Macht! Ihr anderen Kohlenhydrate könnt einpacken. 👑🍟"
            ]
            await message.reply(random.choice(antworten))

        elif any(word in content for word in ["knusper", "knusprig"]):
            antworten = [
                "Knusprig ist mein zweiter Vorname. Der erste ist Perfektion. ✨🍟",
                "Genau so muss das sein! Außen Gold, innen weich – wie eine echte Königin. 👑"
            ]
            await message.reply(random.choice(antworten))

        elif any(word in content for word in ["rage", "tilt", "ausraster", "sauer"]):
            antworten = [
                "Wer rastet hier?! Wenn hier jemand ausrastet, dann bin ich das, weil meine Frittösenschubse wieder trödelt! 🔥💢",
                "Rage-Modus aktiviert? Atmet durch, Kinder, die Queen regelt das. 🍟😤"
            ]
            await message.reply(random.choice(antworten))

async def setup(bot):
    await bot.add_cog(AutoReply(bot))