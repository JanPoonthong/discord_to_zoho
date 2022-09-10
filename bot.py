import logging
import os

import discord

import file_management
import zoho

logger = logging.getLogger("discord")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(
    filename="discord.log", encoding="utf-8", mode="w"
)
handler.setFormatter(
    logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
)
logger.addHandler(handler)

client = discord.Client(intents=discord.Intents.default())

folder_list = zoho.list_folders_zoho()


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}.")


@client.event
async def on_message(message: discord.Message):
    channel = client.get_channel(int(os.getenv("channel_id")))
    messages = [message async for message in channel.history(limit=200)]
    await file_management.save_image_on_local(messages)
    for folder_name in folder_list:
        zoho.save_zoho_drive(folder_list[folder_name], folder_name)
