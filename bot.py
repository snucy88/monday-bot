import discord
import os
import time
from openai import OpenAI
from logic.prompts import PROMPT
from logic.triggers import has_trigger
from logic.context_handler import is_followup, update_context
from logic.memory import init_user, remember_fact, remember_like, update_topic, get_user_profile
from logic.cloud_history import add_to_history
from logic.vector_store import save_embedding, query_similar_messages  # NEU
from logic.embedding import get_embedding  # NEU

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

openai_client = OpenAI(api_key=OPENAI_API_KEY)

active_conversations = {}  # { user_id: (is_active, timestamp) }
CONVO_TIMEOUT = 600  # 10 Minuten

@client.event
async def on_ready():
    print(f"{client.user} ist online – zynisch, wach und bereit.")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    user_id = str(message.author.id)
    username = message.author.display_name
    content = message.content.strip()

    init_user(user_id, username)

    lowered = content.lower()
    if "kaffee" in lowered:
        remember_like(user_id, "Kaffee")
        update_topic(user_id, "Kaffee")
    if "stress" in lowered or "notfall" in lowered:
        remember_fact(user_id, "arbeitet im Notfall oder ist gestresst")
        update_topic(user_id, "Stress")
    if "ich hasse" in lowered:
        h = lowered.split("ich hasse")[-1].strip()
        remember_fact(user_id, f"hasst: {h}")
        update_topic(user_id, "Hass")
    if "ich liebe" in lowered or "ich mag" in lowered:
        l = lowered.split("ich liebe")[-1].strip() if "ich liebe" in lowered else lowered.split("ich mag")[-1].strip()
        remember_like(user_id, l)
        update_topic(user_id, "Liebe")

    now = time.time()
    is_active, last_time = active_conversations.get(user_id, (False, 0))
    timed_out = now - last_time > CONVO_TIMEOUT
    name_mentioned = client.user.mentioned_in(message) or "monday" in lowered

    should_respond = (
        name_mentioned
        or has_trigger(lowered)
        or is_followup(user_id, lowered)
        or (is_active and not timed_out)
    )

    if should_respond:
        active_conversations[user_id] = (True, now)
        try:
            embedding = get_embedding(content)
            similar_context = query_similar_messages(user_id, embedding, limit=3)

            messages = [
                {"role": "system", "content": PROMPT}
            ] + [
                {"role": "user", "content": entry['message']} for entry in similar_context
            ] + [
                {"role": "user", "content": content}
            ]

            response = openai_client.chat.completions.create(
                model="gpt-4",
                messages=messages
            )
            reply = response.choices[0].message.content
            await message.channel.send(reply)

            update_context(user_id)
            add_to_history(user_id, username, content, reply)
            save_embedding(user_id, username, content, embedding.tolist())

        except Exception as e:
            await message.channel.send(f"Ich bin verwirrt. Wie du. ({e})")

client.run(DISCORD_TOKEN)
