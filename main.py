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

client = discord.Client()


@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))


@client.event
async def on_message(message: discord.Message):
    channel = discord.utils.get(message.guild.text_channels, name="general")
    messages = await channel.history(limit=5).flatten()

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


async def download_image(url: str, images_path: str = ""):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                image_name = os.path.basename(url)
                with open(os.path.join(images_path, image_name), "wb") as f:
                    f.write(await resp.read())


client.run(os.getenv("TOKEN"))
