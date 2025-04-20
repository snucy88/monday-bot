import discord
import os
from openai import OpenAI
from logic.prompts import PROMPT
from logic.triggers import has_trigger
from logic.context_handler import is_followup, update_context, reset_context

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

    msg = message.content.lower()
    reset_context_if_new_user(message.author.id)

    if (
        client.user.mentioned_in(message)
        or has_trigger(msg)
        or is_followup(message.author.id, msg)
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