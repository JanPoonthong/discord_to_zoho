import discord
import logging
import os

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("discord")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(
    filename="discord.log", encoding="utf-8", mode="w"
)
handler.setFormatter(
    logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
)
logger.addHandler(handler)

client = discord.Client()


@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))


@client.event
async def on_message(message):
    channel = discord.utils.get(message.guild.text_channels, name="general")
    messages = await channel.history(limit=1).flatten()
    print(messages[0])

    if message.author == client.user:
        return

    if message.content.startswith("$hello"):
        await message.channel.send("Hello!")

    if message.attachments != None:
        print(message.attachments[0].filename)
        print(message.attachments[0].url)


client.run(os.getenv("TOKEN"))
