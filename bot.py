import os
import random
import datetime
import discord
from discord.ext import commands
from flask import Flask
from threading import Thread
from dotenv import load_dotenv

# ==========================================
# 1. SETUP FOR LOCAL PC & RENDER SERVER
# ==========================================

load_dotenv()

app = Flask('')

@app.route('/')
def home():
    return "Pommse ist online und frittiert!"

def run():
    app.run(host='0.0.0.0', port=10000)

Thread(target=run).start()

# ==========================================
# 2. DISCORD BOT INTENTS & BOT-INSTANZ
# ==========================================

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Erlaubt das Ändern von Spitznamen & Rollen

bot = commands.Bot(command_prefix="!", intents=intents)


# ==========================================
# EVENTS
# ==========================================

@bot.event
async def on_ready():
    print(f"🍟 Pommse ist am Start und bereit zum Frittieren! (Eingeloggt als {bot.user})")
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="wie du tiltest 🧂"
        )
    )


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    msg = message.content.lower()

    if "pommes" in msg:
        await message.add_reaction("🍟")
        await message.add_reaction("🥫")

    if "hunger" in msg:
        await message.channel.send("Did somebody say... **POMMES**? 🍟")

    if "tilt" in msg or "rage" in msg:
        await message.add_reaction("🧂")
        await message.channel.send(
            f"⚠️ *Salzgehalt im Chat steigt...* {message.author.mention}"
        )

    if bot.user.mentioned_in(message) and not message.mention_everyone:
        konter = [
            "Was willst du denn, du halbgare Fritte? 🍟",
            f"Red nicht so viel, sonst wirst du ganz matschig, {message.author.mention}!",
            "Lass mich in Ruhe, ich bin gerade auf 180 Grad Betriebstemperatur. 🛢️",
            "Du bist doch auch nur 'ne ungewaschene Kartoffel... 🥔",
        ]
        await message.channel.send(random.choice(konter))

    await bot.process_commands(message)


# ==========================================
# SPITZNAMEN- & ROLLEN-FEATURES
# ==========================================

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

# Spitznamen-Command (Ändert den Server-Namen)
@bot.command(name="spitzname", aliases=["nickname", "taufe"])
@commands.has_permissions(manage_nicknames=True)
async def spitzname(ctx, member: discord.Member = None):
    target = member if member else ctx.author
    neuer_name = random.choice(SPITZNAMEN_LISTE)

    try:
        await target.edit(nick=neuer_name)
        await ctx.send(f"🍟 **Feierliche Fritten-Taufe!** {target.mention} heißt ab sofort offiziell: **{neuer_name}**!")
    except discord.Forbidden:
        await ctx.send("❌ Mir fehlen die Rechte! Meine Rolle muss höher liegen als die der Person und das Recht 'Spitznamen verwalten' haben.")
    except Exception as e:
        await ctx.send(f"❌ Fehler: {e}")
        
# Spitznamen einfach nur im Chat RUFEN
@bot.command(name="rufname", aliases=["ruf", "spitznamen"])
async def rufname(ctx, member: discord.Member = None):
    target = member.mention if member else ctx.author.mention
    vorsatz = [
        "Für mich bist und bleibst du einfach",
        "Mein Fritten-Gefühl nennt dich ab heute",
        "Achtung, jetzt kommt dein neuer Rufname:",
        "Dich nenne ich ab jetzt nur noch",
    ]
    name = random.choice(SPITZNAMEN_LISTE)
    await ctx.send(f"🍟 {target} – {random.choice(vorsatz)} **{name}**!")


# DIE STAMMGAST-VERGABE (Rollen-Command)
@bot.command(name="stammgast")
@commands.has_permissions(administrator=True)
async def stammgast(ctx, member: discord.Member):
    role_name = "Stammgast"
    role = discord.utils.get(ctx.guild.roles, name=role_name)

    if not role:
        await ctx.send(
            f"🍟 Ups! Die Rolle '{role_name}' existiert auf diesem Server noch gar nicht. Leg sie mal kurz an!"
        )
        return

    try:
        await member.add_roles(role)
        await ctx.send(
            f"🎉 Frittier-Ehrenwort! {member.mention} hat offiziell die {role_name}-Rolle bekommen und gehört jetzt zum harten Kern der Fritöse!"
        )
    except discord.Forbidden:
        await ctx.send(
            "⚠️ Mir fehlen die Rechte! Schieb meine Bot-Rolle in den Server-Einstellungen ganz nach oben."
        )


# ==========================================
# SPECIAL-COMMANDS
# ==========================================

@bot.command(name="orakel", aliases=["frage", "8ball"])
async def orakel(ctx, *, frage: str = None):
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
    
    
@bot.command(name="fett")
async def fett(ctx, *, thema: str = None):
    prozent = random.randint(12, 99)
    ziel = thema if thema else f"{ctx.author.mention}"
    
    await ctx.send(
        f"🧪 **Fettgehalt-Analyse für {ziel}:**\n"
        f"Das hat einen Fettgehalt von **{prozent}%**! "
        f"{'Absolut ungesund, aber geil! 🔥' if prozent > 50 else 'Geht eigentlich, wie eine leichte Gemüsepommes. 🥦'}"
    )

@bot.command(name="roulette")
async def roulette(ctx):
    ergebnisse = [
        "🍟 **Perfekt!** Du hast eine goldbraune, knusprige Riffelpommse gezogen. +50 Knusper-Punkte!",
        "🥤 **Glück gehabt!** Nur eine lauwarme Pommes aber mit extra Mayo.",
        "🔥 **AIAIAI!** Zu nah an die Fritteuse geraten. Du hast dir die Finger verbrannt!",
        "💀 **ABSTURZ!** Du bist direkt ins 180°C heiße Fett gefallen. Absoluter Totalschaden!",
        "🥔 **Kartoffel-Glück:** Eine perfekte Süßkartoffel-Fritte! Knusprigkeits-Level 100.",
    ]
    await ctx.send(
        f"🎰 {ctx.author.mention} dreht am Fritteusen-Rad...\n\n{random.choice(ergebnisse)}"
    )

@bot.command(name="horoskop", aliases=["schicksal"])
async def horoskop(ctx):
    horoskope = [
        "Heute gelingt dir jeder Headshot – du bist knackiger unterwegs als frische Fritten nach der Nachtschicht!",
        "Vorsicht heute: Dein Aim wird so schwammig sein wie eine Pommes, die 4 Stunden in der Papiertüte lag.",
        "Die Sterne stehen gut: Wenn du heute verlierst, schieb es einfach aufs fehlende Ketchup.",
        "Heute droht hoher Salzgehalt! Mach lieber nach jedem Match 5 Minuten Pause.",
        "Das Fritten-Schicksal lächelt dir zu: Ein meisterhafter Tag wartet auf dich!",
    ]
    await ctx.send(
        f"🔮 **Fritten-Horoskop für {ctx.author.mention}:**\n_{random.choice(horoskope)}_"
    )

@bot.command(name="rezept")
async def rezept(ctx):
    zot1 = ["Süßkartoffel-Fritten", "Gitterkartoffeln", "Klassische Pommes", "Chili-Cheese-Fries", "Wellenschnitt-Fritten"]
    zot2 = ["mit Nutella", "getunkt in Energy-Drink", "mit Extra-Knoblauch-Mayo", "überstreut mit Gummibärchen", "überbacken mit Schmelzkäse"]
    zot3 = ["und einer Prise Speisesalz.", "und warmem Maggi.", "garniert mit Pfefferminz-Eis.", "serviert in einer Zeitung von gestern."]

    await ctx.send(
        f"👨‍🍳 **Pommse' Chef-Empfehlung:**\n{random.choice(zot1)} {random.choice(zot2)} {random.choice(zot3)}"
    )

# USER NECKEN / BELEIDIGEN
@bot.command(name="necken", aliases=["neck", "beleidige"])
async def necken(ctx, member: discord.Member = None):
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
        "Du bist so durchgeschwitzt, du schmeckst schon nach Rapsöl!",
        "Nicht mal die Möwen am Kiosk würden dich wegpicken! 🕊️",
        # NEUE CHOP-SPRÜCHE 🍟🔥
        "Uiuiui, da ist aber jemand ordentlich versalzen heute! 🧂😳",
        "Oh oh... da denkt wohl jemand, er wäre eine edle Süßkartoffel! 🍠✨",
        "Du bist doch maximal 'ne Riffelfritte auf Sparflamme! 📉",
        "Riechst du das? Du riechst nach 3 Wochen altem Fritteusen-Fett! 🤢",
        "Du hast auch mehr Mayonnaise als Hirn im Kopf, oder? 🥫🧠",
        "Pssssst... leise sein, sonst landest du direkt als Beilage im Kindermenü! 🧸🍟"
    ]
    await ctx.send(f"🍟 {target} – {random.choice(neck_sprueche)}")

@bot.command(name="ping")
async def ping(ctx):
    await ctx.send("Pong! 🏓")

@bot.command(name="kater")
async def kater(ctx):
    kater_sprueche = [
        "Fritteuse auf Notstrom! Du brauchst jetzt drei Liter eiskaltes Leitungswasser und absolute Stille.",
        "Diagnose: Zu viel Gaming, zu wenig Schlaf. Leg dich hin, bevor dein Gehirn durchschmort wie eine alte Pommes.",
        "Hier, nimm eine virtuelle Schmerztablette und einen kalten Kakao. Das wird heute nix mehr mit Aiming.",
    ]
    await ctx.send(f"🤕 {ctx.author.mention} – {random.choice(kater_sprueche)}")

@bot.command(name="entscheide")
async def entscheide(ctx, *, choices: str):
    options = choices.split(" oder ")
    if len(options) < 2:
        await ctx.send(
            "🍟 Hey! Du musst mir schon zwei Dinge mit 'oder' getrennt nennen (z. B. `!entscheide Zocken oder Schlafen`)."
        )
        return
    selected = random.choice(options).strip()
    begruendungen = [
        f"Nimm **{selected}**! Das ist knackig wie 'ne frische Pommes.",
        f"Ganz klar **{selected}**! Alles andere ist aktuell eher wie 'ne halbe Stunde im Fett vergessen.",
        f"Das Fritten-Orakel hat gesprochen: **{selected}**! Vertrau der Fritteuse.",
        f"Ich habe die Kartoffeln befragt... sie sagen eindeutig: **{selected}**!",
    ]
    await ctx.send(f"🍟 {random.choice(begruendungen)}")

@bot.command(name="salz")
async def salz(ctx, member: discord.Member = None):
    target = member.mention if member else "Jemand"
    salz_sprueche = [
        f"Achtung! {target} wird langsam zu salzig für die Tüte. Hier ist ein Kaltgetränk, atme mal kurz durch, sonst wirst du matschig! 🥤",
        f"WARNUNG: Der Salzgehalt bei {target} übersteigt die EU-Grenzwerte! 🧂 Bitte kurz tief durchatmen.",
    ]
    await ctx.send(f"🧂 {random.choice(salz_sprueche)}")

@bot.command(name="feier")
async def feier(ctx):
    titel = ["Die Ketchup-Kanone 🥫", "Der Frittier-Meister 🔥", "Der knusprige Carry 🍟", "Der kalte Erdäpfel 🥔", "Die Mayo-Majestät 👑"]
    await ctx.send(
        f"🎉 **GG WP! FEIERABEND!** 🎉\n"
        f"Pommse schmeißt eine virtuelle Tüte Fritten in die Runde! 🍟✨\n"
        f"MVP der Runde ({ctx.author.mention}) erhält hiermit den Titel: **{random.choice(titel)}**"
    )

@bot.command(name="sauce", aliases=["soße"])
async def sauce(ctx, member: discord.Member = None):
    target = member.mention if member else ctx.author.mention
    
    soessen = [
        "**Klassisch Ketchup** – Verlässlich, bodenständig und ein echter Freund! 🍅",
        "**Mayo Extra Fett** – Ein bisschen drüber, aber alle lieben dich! 🥫",
        "**Joppiesauce** – Süß, würzig und extrem speziell! 🇳🇱",
        "**Knoblauch-Sauce** – Sehr stabil, aber halte heute lieber Abstand zu Leuten! 🧄",
        "**Scharfe Chili-Sauce** – Vorsicht, heute bist du richtig feurig unterwegs! 🔥",
        "**Trüffel-Mayo** – Hui, da hält sich wohl jemand für was Besseres! 💅✨",
        "**Süß-Sauer** – Heute bist du eine emotionale Achterbahnfahrt! 🎢"
    ]
    await ctx.send(f"🧪 {target}, deine Sauce des Tages ist: {random.choice(soessen)}")
    
    
@bot.command(name="quiz")
async def quiz(ctx):
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

@bot.command(name="matsch")
async def matsch(ctx, member: discord.Member = None):
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

@bot.command(name="muenze", aliases=["flip", "ketchupodermayo"])
async def muenze(ctx):
    ergebnis = random.choice(["🍅 **KETCHUP!**", "🥫 **MAYO!**"])
    await ctx.send(f"🪙 Die Münze fliegt durch die Fritteuse und landet auf... {ergebnis}")
    
@bot.command(name="slots", aliases=["casino", "zocken"])
async def slots(ctx):
    emojis = ["🍟", "🥔", "🧀", "🌭", "🧂", "🍠"]
    slot1 = random.choice(emojis)
    slot2 = random.choice(emojis)
    slot3 = random.choice(emojis)
    
    zeile = f"🎰 | {slot1} | {slot2} | {slot3} |\n\n"
    
    if slot1 == slot2 == slot3:
        await ctx.send(f"{zeile}🎉 **JACKPOT!** Du gewinnst eine lebenslange Flatrate für Riffelfritten! 🏆🍟")
    elif slot1 == slot2 or slot2 == slot3 or slot1 == slot3:
        await ctx.send(f"{zeile}✨ Fast! Zwei gleiche! Hier ist ein Trost-Ketchup. 🍅")
    else:
        await ctx.send(f"{zeile}💀 Nichts getroffen! Deine Pommes ist ins Fett gefallen.")
        
# USER IN DIE FRITTEUSE SCHICKEN (TIMEOUT)
@bot.command(name="fritteuse", aliases=["timeout", "auszeit", "frittieren"])
@commands.has_permissions(moderate_members=True) # Nur Admins/Moderatoren dürfen das
async def fritteuse(ctx, member: discord.Member, minuten: int = 5, *, grund: str = "Zu salzig gewesen"):
    """Nutzung: !fritteuse @User [Minuten] [Grund]
    Beispiel: !fritteuse @NervigerUser 10 Spamming
    """
    if member == ctx.author:
        await ctx.send("🍟 Du kannst dich doch nicht selbst frittieren, du Knusperkopf!")
        return

    # Zeitdauer umrechnen
    dauer = discord.utils.utcnow() + datetime.timedelta(minutes=minuten)

    try:
        # Führt das Discord-Timeout aus
        await member.timeout(dauer, reason=grund)
        await ctx.send(
            f"🔥 **AB IN DIE FRITTEUSE!** {member.mention} wurde für **{minuten} Minute(n)** auf 180°C runtergekühlt!\n"
            f"💬 *Grund:* {grund}\n"
            f"🤫 *Das war's erst mal, ab in die Fritten mit dir!*"
        )
    except discord.Forbidden:
        await ctx.send("❌ Mir fehlen die Rechte! Meine Bot-Rolle muss höher liegen als die des Ziel-Users.")
    except Exception as e:
        await ctx.send(f"❌ Fehler beim Frittieren: {e}")

# USER VORZEITIG AUS DER FRITTEUSE HOLE (TIMEOUT ENTFERNEN)
@bot.command(name="entfrittieren", aliases=["unmute", "rausholen"])
@commands.has_permissions(moderate_members=True)
async def entfrittieren(ctx, member: discord.Member):
    """Nutzung: !entfrittieren @User"""
    try:
        # Timeout aufheben (None setzt die Zeit zurück)
        await member.timeout(None)
        await ctx.send(
            f"🍟 **Frisch abgetropft!** {member.mention} wurde vorzeitig aus der Fritteuse geholt und darf wieder mitreden."
        )
    except discord.Forbidden:
        await ctx.send("❌ Mir fehlen die Rechte dafür!")
    except Exception as e:
        await ctx.send(f"❌ Fehler: {e}")

# ==========================================
# BOT STARTEN
# ==========================================
TOKEN = os.getenv("HAUPTBOT_DISCORD_TOKEN")

if TOKEN:
    bot.run(TOKEN)
else:
    print("⚠️ Kein Token gefunden!")