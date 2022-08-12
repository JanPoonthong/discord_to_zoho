import discord
import logging
import os
import requests


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
    # channel = discord.utils.get(message.guild.text_channels, name="general")
    # messages = await channel.history(limit=1).flatten()

    if message.author == client.user:
        return

    if message.content.startswith("$hello"):
        await message.channel.send("Love you Shan!")
    
    if len(message.attachments) > 0:
            attachment = message.attachments[0]
    
    if attachment.filename.endswith(".jpg") or attachment.filename.endswith(".jpeg") or attachment.filename.endswith(".png") or attachment.filename.endswith(".webp") or attachment.filename.endswith(".gif"):
        img_data = requests.get(attachment.url).content
        with open('image_name.jpg', 'wb') as handler:
            handler.write(img_data)

    elif "https://images-ext-1.discordapp.net" in message.content or "https://tenor.com/view/" in message.content:
        print(message.content)


client.run(os.getenv("TOKEN"))
