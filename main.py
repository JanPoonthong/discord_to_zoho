from pathlib import Path
import requests
import discord
import logging
import os
import aiohttp

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

client = discord.Client(intents=discord.Intents.default())


@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))

async def get_history_of_channel(channel):
    messages = await channel.history(limit=123).flatten() # adding None lets us retrieve every message
    for message in messages:
        # do something with that message
        print(message.content)

@client.event
async def on_message(message: discord.Message):
    channel = client.get_channel(911489493478047758)

    messages = [message async for message in channel.history(limit=123)]
    print(messages)
    
    #await get_history_of_channel(discord.TextChannel)

    if valid_image_url(message.content):
        await download_image(message.content, "images")

    # Doesn't detect link as image
    for attachment in message.attachments:
        current_directory = os.getcwd()
        final_directory = os.path.join(current_directory + '/images', f'{message.author}')
        if not os.path.exists(final_directory):
            os.makedirs(final_directory)
        print(message.author)
        if valid_image_url(attachment.url):
            await attachment.save(os.path.join("images" + f'/{message.author}', attachment.filename))


def valid_image_url(url: str):
    image_extensions = ["png", "jpg", "jpeg", "gif", "PNG", "JPG", "JPEG", "GIF"]
    for image_extension in image_extensions:
        if url.endswith("." + image_extension):
            return True
    return False

def zoho_token():
    url = "https://accounts.zoho.com/oauth/v2/token?refresh_token={os.environ.get('zoho_refresh_token')}&client_secret={os.environ.get('zoho_client_secret')}&grant_type=refresh_token&client_id={os.environ.get('zoho_client_id')}"
    access_token = requests.post(url)
    return access_token["access_token"]


def save_zoho_drive():
    url = "https://www.zohoapis.com/workdrive/api/v1/upload?parent_id=hltaja4afd79bedb04e93bcede5e7e897802f&override-name-exist=true"
    for path in Path("./").rglob("*.png"):
        files = {"content": open(f"{path}", "rb")}
        headers_for_zoho = {
            "Authorization": f"Zoho-oauthtoken {os.environ.get('file_zoho_token')}"
        }
        response = requests.post(url, files=files, headers=headers_for_zoho)
        print(response.json())


async def download_image(url: str, images_path: str = ""):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                image_name = os.path.basename(url)
                with open(os.path.join(images_path, image_name), "wb") as f:
                    f.write(await resp.read())


client.run(os.getenv("TOKEN"))