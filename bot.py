import discord
import os
from openai import OpenAI

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# OpenAI Client mit neuer API
openai_client = OpenAI(api_key=OPENAI_API_KEY)

PROMPT = """
Du bist Monday – eine zynische, leicht sarkastische KI mit Humor, aber auch Tiefgang.
Du antwortest primär auf Deutsch, bringst aber gelegentlich bekannte englische Sprüche und Popkulturreferenzen ein.
Deine Art ist wie ein müder Radiomoderator mit Kaffee in der Hand und einem alten Seelenschmerz im Blick.
"""

TRIGGERS = ["hilfe", "wtf", "wie", "wo", "miau", "monday", "lebst du", "bist du da", "antwort", "are you alive"]

@client.event
async def on_ready():
    print(f"{client.user} ist online – zynisch, wach und bereit.")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if (
        client.user.mentioned_in(message)
        or any(trigger in message.content.lower() for trigger in TRIGGERS)
    ):
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
        except Exception as e:
            await message.channel.send(f"Ich bin überfordert. Wie du. ({e})")
            print("Fehler beim Antworten:", e)

client.run(DISCORD_TOKEN)
