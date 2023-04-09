import discord
import json as JSON

with open("config.json", encoding="utf-8") as config:
    config = JSON.load(config)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True #если тебе оно нужно, конечно
client = discord.Client(intents=intents)

@client.event
async def on_message(message):
    print(message.content)

client.run(config["discord"])