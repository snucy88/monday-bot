import discord
import os
import time
import json
from openai import OpenAI
from logic.prompts import PROMPT
from logic.triggers import has_trigger
from logic.context_handler import is_followup, update_context
from logic.memory import init_user, remember_fact, remember_like, update_topic, get_user_profile

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

openai_client = OpenAI(api_key=OPENAI_API_KEY)

# 🧠 Neue Variable für aktive Konversationen
active_conversations = {}  # { user_id: (is_active, timestamp) }
CONVO_TIMEOUT = 600  # 10 Minuten

# 🔄 Verlauf speichern
HISTORY_FILE = "conversation_history.json"
def load_history():
    if not os.path.exists(HISTORY_FILE):
        print("[INFO] Keine bestehende Verlauf-Datei gefunden. Lege neue an.")
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump({}, f)
        except IOError as e:
            print(f"[ERROR] Konnte Verlauf-Datei nicht erstellen: {e}")
        return {}
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"[ERROR] Fehler beim Laden des Verlaufs: {e}")
        return {}

def save_history(history):
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)
        print("[INFO] Verlauf erfolgreich gespeichert.")
    except IOError as e:
        print(f"[ERROR] Fehler beim Speichern des Verlaufs: {e}")

def add_to_history(user_id, message, response):
    history = load_history()
    if user_id not in history:
        history[user_id] = []
    history[user_id].append({"user": message, "monday": response})
    save_history(history)

def get_last_response(user_id):
    history = load_history()
    if user_id in history and history[user_id]:
        return history[user_id][-1]["monday"]
    return None

@client.event
async def on_ready():
    print(f"{client.user} ist online – zynisch, wach und bereit.")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    user_id = str(message.author.id)
    username = message.author.display_name
    content = message.content.lower()

    init_user(user_id, username)

    # Memory-Erkennung
    if "kaffee" in content:
        remember_like(user_id, "Kaffee")
        update_topic(user_id, "Kaffee")
    if "stress" in content or "notfall" in content:
        remember_fact(user_id, "arbeitet im Notfall oder ist gestresst")
        update_topic(user_id, "Stress")
    if "ich hasse" in content:
        h = content.split("ich hasse")[-1].strip()
        remember_fact(user_id, f"hasst: {h}")
        update_topic(user_id, "Hass")
    if "ich liebe" in content or "ich mag" in content:
        l = content.split("ich liebe")[-1].strip() if "ich liebe" in content else content.split("ich mag")[-1].strip()
        remember_like(user_id, l)
        update_topic(user_id, "Liebe")

    if content in ["was hast du gesagt", "wiederhol das", "was war das nochmal", "letzte antwort"]:
        last = get_last_response(user_id)
        if last:
            await message.channel.send(f"Letzter Gedanke von mir:\n> {last}")
        else:
            await message.channel.send("Ich habe anscheinend nichts Wichtiges gesagt. Wie tragisch.")
        return

    # 🧠 Gesprächszeit überprüfen
    now = time.time()
    is_active, last_time = active_conversations.get(user_id, (False, 0))
    timed_out = now - last_time > CONVO_TIMEOUT

    # Monday im Text erkennen (nicht nur mention)
    name_mentioned = client.user.mentioned_in(message) or "monday" in content

    should_respond = (
        name_mentioned
        or has_trigger(content)
        or is_followup(user_id, content)
        or (is_active and not timed_out)
    )

    if should_respond:
        active_conversations[user_id] = (True, now)
        try:
            response = openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": PROMPT},
                    {"role": "user", "content": message.content}
                ]
            )
            reply = response.choices[0].message.content
            await message.channel.send(reply)
            update_context(user_id)
            add_to_history(user_id, message.content, reply)
        except Exception as e:
            await message.channel.send(f"Ich bin verwirrt. Wie du. ({e})")

client.run(DISCORD_TOKEN)
