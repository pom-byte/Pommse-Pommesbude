import discord
from discord.ext import commands

class AnleitungCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="anleitung")
    @commands.has_permissions(administrator=True)
    async def anleitung_command(self, ctx):
        # -------------------------------------------------------------
        # TRAGE HIER DEINE ECHTE ANLEITUNGS-KANAL-ID EIN
        # -------------------------------------------------------------
        ANLEITUNG_CHANNEL_ID = 15331874594863226988  # <--- HIER DEINE ID REIN!
        
        target_channel = self.bot.get_channel(ANLEITUNG_CHANNEL_ID)
        if not target_channel:
            target_channel = ctx.channel

        embed = discord.Embed(
            title="📖 POMMSE-BOT — OFFIZIELLE ANLEITUNG & BEFEHLE 🍟",
            description=(
                "Willkommen in der Frittenschmiede! Hier findest du alle aktiven Befehle, "
                "um deine Knusper-Punkte zu scheffeln, deine Pets zu versorgen und den Bot zu nutzen:\n\n"
                
                "💰 **Economy & Punkte**\n"
                "• `!daily` – Hole dir deine tägliche Frittier-Ration ab (+50 Knusper-Punkte & Highscore-Bonus).\n"
                "• `!punkte` (oder `!knusper`, `!score`, `!profil`) – Zeigt dein Fritten-Profil.\n"
                "• `!rangliste` (oder `!leaderboard`, `!top`) – Zeigt die Top 10 Legenden nach Highscore (⭐).\n"
                "• `!give <@User> <Anzahl>` (oder `!trinkgeld`, `!schenken`) – Punkte an andere rüberschieben.\n\n"
                
                "🎰 **Spiele & Glücksspiel**\n"
                "• `!ssp <schere/stein/papier> [einsatz]` – Schere, Stein, Papier gegen den Bot.\n"
                "• `!roulette <einsatz> <rot/schwarz/zahl>` – Roulette spielen (Zahlen 0–36 zahlen 35:1!).\n\n"
                
                "🐾 **Pets, Menü & Shop**\n"
                "• `!menue` (oder `!shop`, `!speisekarte`) – Speisekarte für Accessoires und Items.\n"
                "• `!kaufen <item>` – Kaufe stylische Items (Sonnenbrille, Hütchen etc.) für dein Pet.\n\n"
                
                "🎉 **Spaß & Fun-Befehle**\n"
                "• `!spitzname` / `!rufname` – Verleiht oder zeigt Fritten-Spitznamen.\n"
                "• `!orakel <Frage>` – Befragt das allwissende Fett-Orakel.\n"
                "• `!fett [Thema]` – Analysiert den prozentualen Fettgehalt.\n"
                "• `!horoskop` / `!rezept` – Fritten-Schicksal und Chef-Empfehlungen.\n"
                "• `!necken <@User>` / `!salz <@User>` – Locksprüche und Salz-Warnungen.\n"
                "• `!ping` / `!kater` / `!entscheide <A> oder <B>` – Hilfreiches & Schnelles.\n"
                "• `!feier` / `!sauce` / `!quiz` / `!matsch` – Mehr Spaß für die Community.\n"
                "• `!muenze` / `!kompliment` / `!dippen` – Münzwurf, Liebe und heiße Flirts."
            ),
            color=discord.Color.orange()
        )
        embed.set_footer(text="pom.world Frittenschmiede | Offizielle Bot-Dokumentation 🍟")

        try:
            await ctx.message.delete()
        except:
            pass

        await target_channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(AnleitungCog(bot))