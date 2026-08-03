import discord
from discord.ext import commands
import os
import psycopg2

def get_db_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"), sslmode='require')

class Achievements(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.init_db()

    def init_db(self):
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Tabelle für alle möglichen Achievements + Pommses Sprüche dazu
            cur.execute("""
                CREATE TABLE IF NOT EXISTS achievements_liste (
                    id SERIAL PRIMARY KEY,
                    key_name TEXT UNIQUE,
                    titel TEXT,
                    beschreibung TEXT,
                    pommse_spruch TEXT
                );
            """)
            
            # Tabelle welche User welche Achievements freigeschaltet haben
            cur.execute("""
                CREATE TABLE IF NOT EXISTS user_achievements (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT,
                    achievement_key TEXT,
                    zeitpunkt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()

            # Ein paar herrlich uff-mäßige Standard-Achievements einfügen (falls noch nicht da)
            default_achievements = [
                ("erster_muell", "Der erste Schrott", "Du hast deinen ersten Müll im Dungeon gefunden.", "Du findest Müll und freust dich auch noch? Ich bewundere deine niedrigen Ansprüche."),
                ("muellverkaeufer", "Recycling-Profi", "Du hast deinen Müll im Pfandhaus verscherbelt.", "Du verkaufst also deinen eigenen Unrat. Kapitalismus im Endstadium, ich liebe es."),
                ("pechvogel", "Bodenkontakt", "Du hast eine epische 1 gewürfelt.", "Eine 1. Du hast den Boden gefunden. Er hat dich vermutlich ausgelacht."),
                ("glueckspilz", "Glücksritter", "Du hast eine natürliche 20 gewürfelt!", "Eine 20?! Wer hat denn hier an den Einstellungen gedreht? Das war pure Bestechung."),
                ("alufolie", "High-Tech-Schutz", "Du hast einen Ritterhelm aus Alufolie ergattert.", "Ein Helm aus Alufolie. Damit schützt du dich vor 5G und schlechtem Geschmack gleichermaßen.")
            ]

            for key, titel, beschreibung, spruch in default_achievements:
                cur.execute("""
                    INSERT INTO achievements_liste (key_name, titel, beschreibung, pommse_spruch) 
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (key_name) DO NOTHING;
                """, (key, titel, beschreibung, spruch))

            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            print(f"Fehler bei DB-Init in Achievements: {e}")

    @commands.command(name="achievements", aliases=["erfolge", "trophaeen"])
    async def achievements(self, ctx, member: discord.Member = None):
        target = member or ctx.author
        user_id = target.id

        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Alle verfügbaren Achievements holen
            cur.execute("SELECT key_name, titel, beschreibung, pommse_spruch FROM achievements_liste;")
            alle = cur.fetchall()
            
            # Freigeschaltete des Users holen
            cur.execute("SELECT achievement_key FROM user_achievements WHERE user_id = %s;", (user_id,))
            freigeschaltet = {row[0] for row in cur.fetchall()}
            
            cur.close()
            conn.close()
        except Exception as e:
            await ctx.send("Datenbankfehler bei den Achievements. Pommse streikt gerade.")
            print(f"Fehler bei !achievements: {e}")
            return

        embed = discord.Embed(
            title=f"🏆 Ruhmeshalle & Fassungslosigkeit von {target.name}",
            description="Hier sind die Meilensteine – und Pommses ehrliche (meist schockierte) Meinung dazu.",
            color=discord.Color.purple()
        )

        erreicht_zaehler = 0
        gesamt_zaehler = len(alle)

        for key, titel, beschreibung, spruch in alle:
            if key in freigeschaltet:
                status = "✅ **Freigeschaltet**"
                erreicht_zaehler += 1
            else:
                status = "🔒 *Gesperrt*"

            feld_wert = f"{beschreibung}\n*{status}*\n💬 *Pommse:* \"{spruch}\""
            embed.add_field(name=f"{titel}", value=feld_wert, inline=False)

        embed.set_footer(text=f"Fortschritt: {erreicht_zaehler} / {gesamt_zaehler} Erfolgen. Respekt ist anders.")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Achievements(bot))