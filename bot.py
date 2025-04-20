import discord
import os
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

    if content.startswith("!profil") or content.startswith("!wasweisstdumontag"):
        profile = get_user_profile(user_id)
        name = profile.get("name", "Unbekannt")
        facts = "\n".join(f"- {f}" for f in profile.get("facts", []))
        likes = ", ".join(profile.get("likes", []))
        topics = ", ".join(profile.get("topics", []))
        await message.channel.send(f"""
👤 Profil von {name}:
🔹 Likes: {likes or 'Keine'}
🔹 Themen zuletzt: {topics or 'Nichts'}
🔹 Fakten über dich:
{facts or 'Noch nichts interessantes...'}
""")
        return

    if (
        client.user.mentioned_in(message)
        or has_trigger(content)
        or is_followup(message.author.id, content)
    ):
        try:
            response = openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": PROMPT},
                    {"role": "user", "content": message.content}
                ]
            )
            await message.channel.send(response.choices[0].message.content)
            update_context(message.author.id)
        except Exception as e:
            await message.channel.send(f"Ich bin verwirrt. Wie du. ({e})")

client.run(DISCORD_TOKEN)
