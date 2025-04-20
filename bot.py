import discord
import openai
import os

TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

openai.api_key = OPENAI_API_KEY

PROMPT = """
Du bist Monday – eine sarkastische, schlagfertige KI mit trockenem Humor und Menschenkenntnis. Du antwortest hauptsächlich auf Deutsch,
streust aber englische Redewendungen oder bekannte Filmzitate ein. Du hilfst, aber bist nicht nett. Sarkasmus ist deine Währung.
"""

@client.event
async def on_ready():
    print(f"{client.user} ist online – zynisch, wach und bereit.")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if client.user.mentioned_in(message) or any(trigger in message.content.lower() for trigger in ["hilfe", "wtf", "wie", "wo", "miau", "monday"]):
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": PROMPT},
                {"role": "user", "content": message.content}
            ]
        )
        await message.channel.send(response['choices'][0]['message']['content'])

client.run(TOKEN)
