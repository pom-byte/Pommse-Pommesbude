import os
import random
import datetime
import discord
from discord.ext import commands
from flask import Flask
from threading import Thread
from dotenv import load_dotenv
import sqlite3

# --- DATENBANK FUNKTIONEN ---
def init_db():
    conn = sqlite3.connect("knusper.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_punkte (
            user_id INTEGER PRIMARY KEY,
            punkte INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def add_punkte(user_id, anzahl):
    conn = sqlite3.connect("knusper.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO user_punkte (user_id, punkte) VALUES (?, 0)", (user_id,))
    cursor.execute("UPDATE user_punkte SET punkte = punkte + ? WHERE user_id = ?", (anzahl, user_id))
    conn.commit()
    conn.close()

def get_punkte(user_id):
    conn = sqlite3.connect("knusper.db")
    cursor = conn.cursor()
    cursor.execute("SELECT punkte FROM user_punkte WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0
    
    
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
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


# ==========================================
# EVENTS
# ==========================================

@bot.event
async def on_ready():
    init_db()
    print(f"🍟 Pommse ist am Start und bereit zum Frittieren! (Eingeloggt as {bot.user})")
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="wie du tiltest 🧂"
        )
    )


@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name="willkommen") 
    if not channel:
        channel = member.guild.text_channels[0]
        
    begruessungen = [
        f"🍟 Hossa {member.mention}! Willkommen in der Frittenschmiede von **pom.world**! Such dir ein warmes Plätzchen am Fettbecken aus.",
        f"🔥 Frischfleisch! {member.mention} hat die Frittenschmiede in pom.world betreten. Mach dich nützlich oder schäl Kartoffeln!",
        f"👑 Willkommen in pom.world, {member.mention}! Hier regieren die Knusprigkeit, die Mayo und ein Admin, der manchmal vergisst, wo der Ein-Schalter ist. Viel Spaß!",
        f"✨ Vorsicht an der Fritteuse, {member.mention} ist da! Willkommen in der heiligen Frittenschmiede von pom.world!"
    ]
    await channel.send(random.choice(begruessungen))


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
# SPECIAL-COMMANDS & UPDATE 0.4
# ==========================================

@bot.command(name="update", aliases=["patchnotes", "pommseupdate"])
@commands.has_permissions(administrator=True)
async def update(ctx, version: str = "0.4"):
    """Pommse verkündet die neuesten Updates und lästert über seine Menschen"""
    target_channel = discord.utils.get(ctx.guild.text_channels, name="👉-updates")
    if not target_channel:
        target_channel = ctx.channel

    story_ueber_menschen = [
        "Mein sogenannter 'Mensch' hat heute mal wieder versucht, Code zu schreiben. Es lief ungefähr so katastrophal wie eine Tiefkühl-Pommes in der Mikrowelle, aber irgendwie hat er es überlebt.",
        "Mein Programmierer saß wieder stundenlang vor dem Bildschirm, hat dreimal den Rechner neu gestartet und behauptet, das wäre 'High-End-Entwicklung'. Na ja, Hauptsache die Fritteuse läuft.",
        "Manchmal tut mein Mensch so, als hätte er alles voll im Griff – und im nächsten Moment vergisst er, wie man ein Terminal schließt. Aber hey, er tippt brav das ein, was ich ihm sage!",
        "Ein großes Lob an meinen Erschaffer: Er hat heute tatsächlich einen ganzen Satz fehlerfrei getippt! Okay, der Bot macht die echte Arbeit, aber man muss die kleinen Erfolge feiern."
    ]

    embed = discord.Embed(
        title=f"🚨 POMMSE UPDATE {version} IST DA! 🚀",
        description=f"**Aus dem Maschinenraum der Frittenschmiede (pom.world):**\n\n*{random.choice(story_ueber_menschen)}*",
        color=discord.Color.gold()
    )
    
    embed.add_field(
        name="🍟 Was ist neu in Update 0.4?",
        value=(
            "• **Echtzeit-Begrüßung:** Jedes neue Frittenglück wird in pom.world nun standesgemäß empfangen!\n"
            "• **Update-Kanal freigeschaltet:** Ab sofort verkündete ich, der allwissende Bot, die Patchnotes selbst.\n"
            "• **Mehr Spice & Flirt:** Die Fritteuse kocht heißer als je zuvor (schaut in den `!dippen`-Befehl! 🔥)\n"
            "• **Stabilität:** Läuft jetzt dank digitalem Wecker 24/7 durch, damit niemand den Stecker zieht."
        ),
        inline=False
    )
    
    # Hier wurde der Text bereinigt (kein Verweis mehr auf KI)
    embed.set_footer(text="pom.world Frittenschmiede | Offizielle Patchnotes")
    
    await target_channel.send(embed=embed)


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
        ("🍟 **Perfekt!** Du hast eine goldbraune, knusprige Riffelpommse gezogen. +50 Knusper-Punkte!", 50),
        ("🥤 **Glück gehabt!** Nur eine lauwarme Pommes aber mit extra Mayo. +10 Knusper-Punkte!", 10),
        ("🔥 **AIAIAI!** Zu nah an die Fritteuse geraten. Du hast dir die Finger verbrannt! -10 Knusper-Punkte!", -10),
        ("💀 **ABSTURZ!** Du bist direkt ins 180°C heiße Fett gefallen. Absoluter Totalschaden! -30 Knusper-Punkte!", -30),
        ("🥔 **Kartoffel-Glück:** Eine perfekte Süßkartoffel-Fritte! Knusprigkeits-Level 100. +100 Knusper-Punkte!", 100),
    ]
    
    text, punkte_wert = random.choice(ergebnisse)
    add_punkte(ctx.author.id, punkte_wert)
    gesammtpunkte = get_punkte(ctx.author.id)
    
    await ctx.send(
        f"🎰 {ctx.author.mention} dreht am Fritteusen-Rad...\n\n{text}\n*(Dein Kontostand: {gesammtpunkte} Knusper-Punkte)*"
    )
    
@bot.command(name="punkte", aliases=["knusper", "score"])
async def punkte_cmd(ctx, member: discord.Member = None):
    target = member if member else ctx.author
    kontostand = get_punkte(target.id)
    await ctx.send(f"🥔 **{target.mention}** besitzt aktuell **{kontostand} Knusper-Punkte** auf dem Fritten-Konto!")

@bot.command(name="rangliste", aliases=["leaderboard", "top"])
async def rangliste(ctx):
    conn = sqlite3.connect("knusper.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, punkte FROM user_punkte ORDER BY punkte DESC LIMIT 10")
    ergebnisse = cursor.fetchall()
    conn.close()

    if not ergebnisse:
        try:
            await ctx.send("🥔 Bisher hat noch niemand Knusper-Punkte gesammelt!")
        except Exception:
            pass
        return

    text = "🏆 **Fritten-Rangliste (Die Top Knusperer):**\n\n"
    for i, (user_id, punkte) in enumerate(ergebnisse, 1):
        user = ctx.guild.get_member(user_id)
        name = user.mention if user else f"User-ID: {user_id}"
        text += f"{i}. {name} – **{punkte} Knusper-Punkte**\n"

    try:
        await ctx.send(text)
    except Exception as e:
        print(f"Fehler beim Senden der Rangliste: {e}")
        
@bot.command(name="horoskop", aliases=["schicksal"])
async def horoskop(ctx):
    horoskope = [
        "Heute gelingt dir jeder Headshot – du bist knackiger unterwegs as frische Fritten nach der Nachtschicht!",
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

@bot.command(name="necken", aliases=["neck", "beleidige"])
async def necken(ctx, member: discord.Member = None):
    target = member.mention if member else ctx.author.mention
    neck_sprueche = [
        "Du halbgare Fritte, du! 🍟",
        "Ganz ehrlich, du bist auch nur 'ne ungewaschene Kartoffel. 🥔",
        "Du wurdest wohl etwas zu lange im kalten Fett vergessen, was? 🛢️",
        "Du hast die Knusprigkeit einer 3 Tage alten Supermarkt-Pommes. 🥴",
        "Dein Aim ist matschiger as 'ne Portion Pommes im Regen. 🌧️🍟",
        "Red weiter, du verbranntes Fritten-Endstück! 🔥",
        "Du fiese Fritte! 🍟",
        "Na, wieder mal im falschen Fett gebadet? 🧼🛢️",
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
    ]
    await ctx.send(f"🤕 {ctx.author.mention} – {random.choice(kater_sprueche)}")

@bot.command(name="entscheide")
async def entscheide(ctx, *, choices: str):
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
    slot1, slot2, slot3 = random.choice(emojis), random.choice(emojis), random.choice(emojis)
    zeile = f"🎰 | {slot1} | {slot2} | {slot3} |\n\n"
    
    if slot1 == slot2 == slot3:
        await ctx.send(f"{zeile}🎉 **JACKPOT!** Du gewinnst eine lebenslange Flatrate für Riffelfritten! 🏆🍟")
    elif slot1 == slot2 or slot2 == slot3 or slot1 == slot3:
        await ctx.send(f"{zeile}✨ Fast! Zwei gleiche! Hier ist ein Trost-Ketchup. 🍅")
    else:
        await ctx.send(f"{zeile}💀 Nichts getroffen! Deine Pommes ist ins Fett gefallen.")
        
@bot.command(name="fritteuse", aliases=["timeout", "auszeit", "frittieren"])
@commands.has_permissions(moderate_members=True)
async def fritteuse(ctx, member: discord.Member, minuten: int = 5, *, grund: str = "Zu salzig gewesen"):
    if member == ctx.author:
        await ctx.send("🍟 Du kannst dich doch nicht selbst frittieren, du Knusperkopf!")
        return

    dauer = discord.utils.utcnow() + datetime.timedelta(minutes=minuten)
    try:
        await member.timeout(dauer, reason=grund)
        await ctx.send(
            f"🔥 **AB IN DIE FRITTEUSE!** {member.mention} wurde für **{minuten} Minute(n)** auf 180°C runtergekühlt!\n"
            f"💬 *Grund:* {grund}"
        )
    except discord.Forbidden:
        await ctx.send("❌ Mir fehlen die Rechte! Meine Bot-Rolle muss höher liegen als die des Ziel-Users.")
    except Exception as e:
        await ctx.send(f"❌ Fehler beim Frittieren: {e}")

@bot.command(name="entfrittieren", aliases=["unmute", "rausholen"])
@commands.has_permissions(moderate_members=True)
async def entfrittieren(ctx, member: discord.Member):
    try:
        await member.timeout(None)
        await ctx.send(f"🍟 **Frisch abgetropft!** {member.mention} wurde vorzeitig aus der Fritteuse geholt und darf wieder mitreden.")
    except discord.Forbidden:
        await ctx.send("❌ Mir fehlen die Rechte dafür!")
    except Exception as e:
        await ctx.send(f"❌ Fehler: {e}")


# ==========================================
# KNUSPER-SHOP & BONUS SYSTEME
# ==========================================

@bot.command(name="daily")
async def daily(ctx):
    conn = sqlite3.connect("knusper.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS user_daily (user_id INTEGER PRIMARY KEY, last_daily TEXT)")
    cursor.execute("SELECT last_daily FROM user_daily WHERE user_id = ?", (ctx.author.id,))
    result = cursor.fetchone()
    heute = datetime.date.today().isoformat()
    
    if result and result[0] == heute:
        conn.close()
        await ctx.send(f"🛑 {ctx.author.mention}, du hast dir deine tägliche Frittier-Ration heute schon abgeholt! Komm morgen wieder.")
        return
        
    add_punkte(ctx.author.id, 50)
    cursor.execute("INSERT OR REPLACE INTO user_daily (user_id, last_daily) VALUES (?, ?)", (ctx.author.id, heute))
    conn.commit()
    conn.close()
    
    gesammt = get_punkte(ctx.author.id)
    await ctx.send(f"🎉 **Tägliche Fritten-Ration abgeholt!** {ctx.author.mention} bekommt **+50 Knusper-Punkte**!\n*(Neuer Kontostand: {gesammt} Punkte)*")


@bot.command(name="give", aliases=["trinkgeld", "schenken"])
async def give(ctx, member: discord.Member, anzahl: int):
    if member == ctx.author:
        await ctx.send("🍟 Du kannst dir doch nicht selbst Punkte schenken, du Schlawiner!")
        return
    if anzahl <= 0:
        await ctx.send("🍟 Du musst schon eine positive Anzahl an Punkten verschenken wollen!")
        return
        
    sender_punkte = get_punkte(ctx.author.id)
    if sender_punkte < anzahl:
        await ctx.send(f"❌ So viele Punkte hast du gar nicht auf dem Konto! (Aktuell: {sender_punkte} Punkte)")
        return
        
    add_punkte(ctx.author.id, -anzahl)
    add_punkte(member.id, anzahl)
    await ctx.send(f"💸 {ctx.author.mention} hat **{anzahl} Knusper-Punkte** an {member.mention} rüberschoben! Stabil! 🤝🍟")


@bot.command(name="cheat", aliases=["adminpunkte", "fabian"])
@commands.has_permissions(administrator=True)
async def cheat(ctx, anzahl: int, member: discord.Member = None):
    target = member if member else ctx.author
    add_punkte(target.id, anzahl)
    neuer_stand = get_punkte(target.id)
    await ctx.send(f"🚨 **ADMIN-CHEAT AKTIVIERT!** {target.mention} hat soeben **{anzahl} Punkte** bekommen!\n*(Kontostand: {neuer_stand} Knusper-Punkte)* 🛢️✨")

@bot.command(name="kompliment", aliases=["frittenlob", "heiss", "ehre"])
async def kompliment(ctx, member: discord.Member = None):
    target = member.mention if member else ctx.author.mention
    komplimente_liste = [
        f"🔥 {target}, du Hottie!",
        f"👑 {target}, absolute Sahnestück-Fritte!",
        f"✨ {target}, du bist knackiger als eine frische Riffelpommse direkt aus dem 180-Grad-Öl!",
        f"🍟 {target}, du Hottie, selbst die edelste Mayo würde vor Neid erblassen, wenn sie dich sieht!",
    ]
    await ctx.send(random.choice(komplimente_liste))
    
@bot.command(name="dippen", aliases=["hotti", "flirt"])
async def dippen(ctx, member: discord.Member = None):
    target = member.mention if member else ctx.author.mention
    flirt_sprueche = [
        f"🌶️ {target}, wenn du eine Pommes wärst, würde ich dich nicht nur in Mayo dippen, sondern in der schärfsten Habanero-Soße baden lassen, bis die Fritteuse kocht!",
        f"🥵 {target}, du brennst so heiß, da schmilzt nicht nur das Rapsöl – du legst hier gerade den ganzen Imbiss lahm!",
        f"🔥 {target}, bei deinem Anblick fängt selbst die kälteste Tiefkühlkost an zu knistern. Wollen wir die Temperatur erhöhen?",
    ]
    await ctx.send(random.choice(flirt_sprueche))
    

# ==========================================
# KNUSPER-MENÜ & BESTELL-SYSTEM
# ==========================================

@bot.command(name="menue", aliases=["shop", "karte"])
async def menue(ctx):
    embed = discord.Embed(
        title="🍟 Pommse' Fritten-Speisekarte",
        description="Tausche deine hart verdienten Knusper-Punkte gegen exklusive Menüs ein!",
        color=discord.Color.orange()
    )
    embed.add_field(name="1. Stammgast-Rolle", value="Kostet: **500 Punkte**\nBestelle mit: `!bestellen stammgast`", inline=False)
    embed.add_field(name="2. Ehren-Fritte Titel", value="Kostet: **200 Punkte**\nBestelle mit: `!bestellen titel`", inline=False)
    embed.set_footer(text="Nutze !bestellen [item] um zuzuschlagen!")
    await ctx.send(embed=embed)


@bot.command(name="bestellen", aliases=["order", "kaufen"])
async def bestellen(ctx, item: str):
    item = item.lower()
    guthaben = get_punkte(ctx.author.id)
    
    if item == "stammgast":
        preis = 500
        if guthaben < preis:
            await ctx.send(f"❌ Zu arm für frittiertes Gold! Du hast {guthaben} Punkte, brauchst aber {preis}.")
            return
            
        role_name = "Stammgast"
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if not role:
            await ctx.send(f"⚠️ Die Rolle '{role_name}' existiert auf dem Server nicht. Leg sie erst an!")
            return
            
        add_punkte(ctx.author.id, -preis)
        await ctx.author.add_roles(role)
        await ctx.send(f"🎉 Frische Bestellung serviert, {ctx.author.mention}! Du hast dir die **Stammgast**-Rolle für {preis} Punkte geschnappt! 👑🍟")
        
    elif item == "titel":
        preis = 200
        if guthaben < preis:
            await ctx.send(f"❌ Dafür reicht dein Kleingeld nicht! Du hast {guthaben} Punkte (Brauchst {preis}).")
            return
            
        add_punkte(ctx.author.id, -preis)
        neuer_titel = "Die Ehren-Fritte 🍟👑"
        try:
            await ctx.author.edit(nick=neuer_titel)
            await ctx.send(f"✨ {ctx.author.mention} hat sich erfolgreich in **{neuer_titel}** umbenennen lassen!")
        except Exception:
            await ctx.send(f"🎉 Punkte abgezogen! (Konnte deinen Spitznamen wegen Admin-Rechten leider nicht ändern, aber der Status gehört dir!)")
    else:
        await ctx.send("❌ Das steht nicht auf der Speisekarte! Tippe `!menue`, um das Angebot zu sehen.")
        
        
# ==========================================
# BOT STARTEN
# ==========================================
TOKEN = os.getenv("HAUPTBOT_DISCORD_TOKEN")

if TOKEN:
    bot.run(TOKEN)
else:
    print("⚠️ Kein Token gefunden!")