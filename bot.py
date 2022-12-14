import logging
import os

import discord

import file_management
import zoho
import datetime

logger = logging.getLogger("discord")
# ENV, all CAP
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(
    filename="discord.log", encoding="utf-8", mode="w"
)
handler.setFormatter(
    logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
)
logger.addHandler(handler)

"""Print in console too"""

client = discord.Client(intents=discord.Intents.default())


print(type(os.getenv("LIMIT_OF_MESSAGE")))


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}.")


@client.event
async def on_message(message: discord.Message):
    channel = client.get_channel(int(os.getenv("channel_id")))
    print("Loading message")
    if os.getenv("NUMBER_OF_MESSAGES") == "None":
        limit = None
    else:
        limit = int(os.getenv("NUMBER_OF_MESSAGES"))
    messages = [message async for message in channel.history(limit=limit)]
    for message in messages:
        if len(message.attachments) > 0:
            print(
                f"Found {len(message.attachments)} attachment in message, saving to zoho"
            )
        for attachment in message.attachments:
            if file_management.valid_image_url(attachment.url):
                print(f"Saving {attachment.filename} in local")
                current_date = datetime.date.today()
                current_time = datetime.datetime.now().strftime("%H%M%S")
                file_name = f"{current_date.strftime('%Y%m%d')}_{current_time}_{message.author}_{attachment.filename}"
                await attachment.save(
                    os.path.join(
                        "/tmp/",
                        file_name,
                    )
                )
                zoho.save_zoho_drive(str(message.author), file_name)
