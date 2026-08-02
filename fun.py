import discord
from discord.ext import commands
import random

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    SPITZNAMEN_LISTE = [
        "curly fries 🌀",
        "Halbgare Fritte 🍟",
        "Mayo-Majestät 👑",
        "Der Knusprige Carry 🔥",
        "Kalte Riffelpommfe 🥔",
        "Salzstreuer 🧂",
        "Doppelt Frittierter 🛢️",
        "Matsch-Erdäpfel 🥴",
        "Ketchup-Kanone 🥫",
        "Trocken-Wedge 🌵",
        "Süß-Sauer-Boss 🍯",
    ]

    @commands.command(name="spitzname", aliases=["nickname", "taufe"])
    @commands.has_permissions(manage_nicknames=True)
    async def spitzname(self, ctx, member: discord.Member = None):
        target = member if member else ctx.author
        neuer_name = random.choice(self.SPITZNAMEN_LISTE)
        try:
            await target.edit(nick=neuer_name)
            await ctx.send(f"🍟 **Feierliche Fritten-Taufe!** {target.mention} heißt ab sofort offiziell: **{neuer_name}**!")
        except discord.Forbidden:
            await ctx.send("❌ Mir fehlen die Rechte! Meine Rolle muss höher liegen als die der Person und das Recht 'Spitznamen verwalten' haben.")
        except Exception as e:
            await ctx.send(f"❌ Fehler: {e}")

    @commands.command(name="rufname", aliases=["ruf", "spitznamen"])
    async def rufname(self, ctx, member: discord.Member = None):
        target = member.mention if member else ctx.author.mention
        vorsatz = [
            "Für mich bist und bleibst du einfach",
            "Mein Fritten-Gefühl nennt dich ab heute",
            "Achtung, jetzt kommt dein neuer Rufname:",
            "Dich nenne ich ab jetzt nur noch",
        ]
        name = random.choice(self.SPITZNAMEN_LISTE)
        await ctx.send(f"🍟 {target} – {random.choice(vorsatz)} **{name}**!")

    @commands.command(name="orakel", aliases=["frage", "8ball"])
    async def orakel(self, ctx, *, frage: str = None):
        if not frage:
            await ctx.send("🍟 Frag das Fett-Orakel etwas! Z.B. `!orakel Werde ich heute gewinnen?`")
            return
        antworten = [
            "Die Fritten-Götter sagen eindeutig: **JA!** ✨🍟",
            "Das Fett blubbert friedlich... das ist ein **Gutes Zeichen**! 🫧",
            "Klarer als frisches Rapsöl: **Auf jeden Fall!** 👍",
            "Puh, die Fritteuse raucht... **Eher nein.** 💨",
            "Matschige Aussichten... **Vergiss es.** 🌧️",
            "Sogar die Süßkartoffeln sind sich uneinig. **Frag später nochmal!** 🍠",
            "Mayonnaise sagt Ja, Ketchup sagt Nein. **50/50!** 🥫"
        ]
        await ctx.send(f"🔮 **Frage:** *{frage}*\n🍟 **Das Orakel sagt:** {random.choice(antworten)}")

    @commands.command(name="fett")
    async def fett(self, ctx, *, thema: str = None):
        prozent = random.randint(12, 99)
        ziel = thema if thema else f"{ctx.author.mention}"
        await ctx.send(
            f"🧪 **Fettgehalt-Analyse für {ziel}:**\n"
            f"Das hat einen Fettgehalt von **{prozent}%**! "
            f"{'Absolut ungesund, aber geil! 🔥' if prozent > 50 else 'Geht eigentlich, wie eine leichte Gemüsepommes. 🥦'}"
        )

    @commands.command(name="horoskop", aliases=["schicksal"])
    async def horoskop(self, ctx):
        horoskope = [
            "Heute gelingt dir jeder Headshot – du bist knackiger unterwegs als frische Fritten nach der Nachtschicht!",
            "Vorsicht heute: Dein Aim wird so schwammig sein wie eine Pommes, die 4 Stunden in der Papiertüte lag.",
            "Die Sterne stehen gut: Wenn du heute verlierst, schieb es einfach aufs fehlende Ketchup.",
            "Heute droht hoher Salzgehalt! Mach lieber nach jedem Match 5 Minuten Pause.",
            "Das Fritten-Schicksal lächelt dir zu: Ein meisterhafter Tag wartet auf dich!",
        ]
        await ctx.send(f"🔮 **Fritten-Horoskop für {ctx.author.mention}:**\n_{random.choice(horoskope)}_")

    @commands.command(name="rezept")
    async def rezept(self, ctx):
        zot1 = ["Süßkartoffel-Fritten", "Gitterkartoffeln", "Klassische Pommes", "Chili-Cheese-Fries", "Wellenschnitt-Fritten"]
        zot2 = ["mit Nutella", "getunkt in Energy-Drink", "mit Extra-Knoblauch-Mayo", "überstreut mit Gummibärchen", "überbacken mit Schmelzkäse"]
        zot3 = ["und einer Prise Speisesalz.", "und warmem Maggi.", "garniert mit Pfefferminz-Eis.", "serviert in einer Zeitung von gestern."]
        await ctx.send(f"👨‍🍳 **Pommse' Chef-Empfehlung:**\n{random.choice(zot1)} {random.choice(zot2)} {random.choice(zot3)}")

    @commands.command(name="necken", aliases=["neck", "beleidige"])
    async def necken(self, ctx, member: discord.Member = None):
        target = member.mention if member else ctx.author.mention
        neck_sprueche = [
            "Du halbgare Fritte, du! 🍟",
            "Ganz ehrlich, du bist auch nur 'ne ungewaschene Kartoffel. 🥔",
            "Du wurdest wohl etwas zu lange im kalten Fett vergessen, was? 🛢️",
            "Du hast die Knusprigkeit einer 3 Tage alten Supermarkt-Pommes. 🥴",
            "Dein Aim ist matschiger als 'ne Portion Pommes im Regen. 🌧️🍟",
            "Red weiter, du verbranntes Fritten-Endstück! 🔥",
            "Du fiese Fritte! 🍟",
            "Na, wieder mal im falschen Fett gebadet? 🧼🛢️",
        ]
        await ctx.send(f"🍟 {target} – {random.choice(neck_sprueche)}")

    @commands.command(name="ping")
    async def ping(self, ctx):
        await ctx.send("Pong! 🏓")

    @commands.command(name="kater")
    async def kater(self, ctx):
        kater_sprueche = [
            "Fritteuse auf Notstrom! Du brauchst jetzt drei Liter eiskaltes Leitungswasser und absolute Stille.",
            "Diagnose: Zu viel Gaming, zu wenig Schlaf. Leg dich hin, bevor dein Gehirn durchschmort wie eine alte Pommes.",
        ]
        await ctx.send(f"🤕 {ctx.author.mention} – {random.choice(kater_sprueche)}")

    @commands.command(name="entscheide")
    async def entscheide(self, ctx, *, choices: str):
        options = choices.split(" oder ")
        if len(options) < 2:
            await ctx.send("🍟 Hey! Du musst mir schon zwei Dinge mit 'oder' getrennt nennen (z. B. `!entscheide Zocken oder Schlafen`).")
            return
        selected = random.choice(options).strip()
        begruendungen = [
            f"Nimm **{selected}**! Das ist knackig wie 'ne frische Pommes.",
            f"Ganz klar **{selected}**! Alles andere ist aktuell eher wie 'ne halbe Stunde im Fett vergessen.",
            f"Das Fritten-Orakel hat gesprochen: **{selected}**! Vertrau der Fritteuse.",
        ]
        await ctx.send(f"🍟 {random.choice(begruendungen)}")

    @commands.command(name="salz")
    async def salz(self, ctx, member: discord.Member = None):
        target = member.mention if member else "Jemand"
        salz_sprueche = [
            f"Achtung! {target} wird langsam zu salzig für die Tüte. Hier ist ein Kaltgetränk, atme mal kurz durch, sonst wirst du matschig! 🥤",
            f"WARNUNG: Der Salzgehalt bei {target} übersteigt die EU-Grenzwerte! 🧂 Bitte kurz tief durchatmen.",
        ]
        await ctx.send(f"🧂 {random.choice(salz_sprueche)}")

    @commands.command(name="feier")
    async def feier(self, ctx):
        titel = ["Die Ketchup-Kanone 🥫", "Der Frittier-Meister 🔥", "Der knusprige Carry 🍟", "Der kalte Erdäpfel 🥔", "Die Mayo-Majestät 👑"]
        await ctx.send(
            f"🎉 **GG WP! FEIERABEND!** 🎉\n"
            f"Pommse schmeißt eine virtuelle Tüte Fritten in die Runde! 🍟✨\n"
            f"MVP der Runde ({ctx.author.mention}) erhält hiermit den Titel: **{random.choice(titel)}**"
        )

    @commands.command(name="sauce", aliases=["soße"])
    async def sauce(self, ctx, member: discord.Member = None):
        target = member.mention if member else ctx.author.mention
        soessen = [
            "**Klassisch Ketchup** – Verlässlich, bodenständig und ein echter Freund! 🍅",
            "**Mayo Extra Fett** – Ein bisschen drüber, aber alle lieben dich! 🥫",
            "**Joppiesauce** – Süß, würzig und extrem speziell! 🇳🇱",
            "**Knoblauch-Sauce** – Sehr stabil, aber halte heute lieber Abstand zu Leuten! 🧄",
            "**Scharfe Chili-Sauce** – Vorsicht, heute bist du richtig feurig unterwegs! 🔥",
        ]
        await ctx.send(f"🧪 {target}, deine Sauce des Tages ist: {random.choice(soessen)}")

    @commands.command(name="quiz")
    async def quiz(self, ctx):
        fragen = [
            ("Wie lang ist die perfekte Pommes?", "a) 7 cm\nb) Egal, hauptsache knusprig\nc) Genau 1 Meter"),
            ("Welches Fett ist das beste?", "a) Frittierfett\nb) Motoröl\nc) Reine Liebe"),
        ]
        frage, antworten = random.choice(fragen)
        embed = discord.Embed(
            title="🍟 Pommse' Unnötiges Quiz",
            description=f"**Frage:** {frage}\n\n{antworten}",
            color=discord.Color.gold(),
        )
        embed.set_footer(text="Die einzig richtige Antwort ist immer B. Vertrau mir.")
        await ctx.send(embed=embed)

    @commands.command(name="matsch")
    async def matsch(self, ctx, member: discord.Member = None):
        target = member if member else ctx.author
        matsch_level = random.randint(0, 100)
        if matsch_level < 20:
            status = "Knackig & frisch aus der Fritteuse! 🍟"
        elif matsch_level < 60:
            status = "Etwas weich, aber noch genießbar. 😐"
        elif matsch_level < 90:
            status = "Schwitzig, matschig, seit 4 Stunden in der Tüte. 🥴"
        else:
            status = "ABSOLUTER MATSCH! Sofort ins Bett legen. 🛑"
        await ctx.send(f"🥔 **Matsch-Analyse für {target.mention}:** {matsch_level}% – *{status}*")

    @commands.command(name="muenze", aliases=["flip", "ketchupodermayo"])
    async def muenze(self, ctx):
        ergebnis = random.choice(["🍅 **KETCHUP!**", "🥫 **MAYO!**"])
        await ctx.send(f"🪙 Die Münze fliegt durch die Fritteuse und landet auf... {ergebnis}")

    @commands.command(name="kompliment", aliases=["frittenlob", "heiss", "ehre"])
    async def kompliment(self, ctx, member: discord.Member = None):
        target = member.mention if member else ctx.author.mention
        komplimente_liste = [
            f"🔥 {target}, du Hottie!",
            f"👑 {target}, absolute Sahnestück-Fritte!",
            f"✨ {target}, du bist knackiger als eine frische Riffelpommse direkt aus dem 180-Grad-Öl!",
            f"🍟 {target}, du Hottie, selbst die edelste Mayo würde vor Neid erblassen, wenn sie dich sieht!",
            f"🥔 {target}, du bist kein normaler Erdäpfel, du bist pure goldbraune Perfektion!",
            f"🌟 {target}, bei dir knuspert's im Herzen – absolute Meisterklasse!",
            f"💎 {target}, du glänzst ja fast so schön wie frisch gewechseltes Rapsöl!",
        ]
        await ctx.send(random.choice(komplimente_liste))

    @commands.command(name="dippen", aliases=["hotti", "flirt"])
    async def dippen(self, ctx, member: discord.Member = None):
        target = member.mention if member else ctx.author.mention
        flirt_sprueche = [
            f"🌶️ {target}, wenn du eine Pommes wärst, würde ich dich nicht nur in Mayo dippen, sondern in der schärfsten Habanero-Soße baden lassen, bis die Fritteuse kocht!",
            f"🥵 {target}, du brennst so heiß, da schmilzt nicht nur das Rapsöl – du legst hier gerade den ganzen Imbiss lahm!",
            f"🔥 {target}, bei deinem Anblick fängt selbst die kälteste Tiefkühlkost an zu knistern. Wollen wir die Temperatur erhöhen?",
            f"🔥 {target}, du machst mich heißer als die heißeste Frittenfettfrittöse!",
            f"❤️‍🔥 {target}, du bringst das Fett zum Blubbern und das Herz zum Schmelzen. Da braucht man gar kein Ketchup mehr!",
            f"🍯 {target}, du bist so süß-scharf, gegen dich ist jede Joppiesauce nur langweiliger Industriedreck!",
            f"⚡ {target}, du stehst so dermaßen unter Strom, du heizt die Fritteuse im Alleingang auf 300 Grad hoch!"
        ]
        await ctx.send(random.choice(flirt_sprueche))

async def setup(bot):
    await bot.add_cog(Fun(bot))