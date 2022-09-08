import json
import logging
import os
from pathlib import Path

import aiohttp
import discord
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

client = discord.Client(intents=discord.Intents.default())


PATH = "images/"
CURRENT_DIRECTORY = os.getcwd()


def create_image_folder_in_local():
    if not os.path.exists(PATH):
        os.mkdir(PATH)


def add_prefix_to_local_folders():
    for folder in DIR_LIST:
        if folder.startswith("user_"):
            continue
        else:
            DIR_LIST.remove(folder)


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}.")


@client.event
async def on_message(message: discord.Message):
    channel = client.get_channel(int(os.getenv("channel_id")))
    messages = [message async for message in channel.history(limit=None)]
    for message in messages:
        for attachment in message.attachments:
            final_directory = os.path.join(
                CURRENT_DIRECTORY + f"/{PATH}", f"user_{message.author}"
            )
            if not os.path.exists(final_directory):
                os.makedirs(final_directory)
            author_images = os.listdir(final_directory)
            files_completed = []
            for image in author_images:
                files_completed.append(image.removeprefix("file_"))
            if attachment.filename in files_completed:
                continue
            if valid_image_url(attachment.url):
                await attachment.save(
                    os.path.join(
                        final_directory,
                        "file_" + attachment.filename,
                    )
                )


def valid_image_url(url: str):
    image_extensions = [
        "png",
        "jpg",
        "jpeg",
        "gif",
        "PNG",
        "JPG",
        "JPEG",
        "GIF",
    ]
    for image_extension in image_extensions:
        if url.endswith("." + image_extension):
            return True
    return False


def generate_zoho_access_token():
    url = f"https://accounts.zoho.com/oauth/v2/token?refresh_token={os.getenv('zoho_refresh_token')}&client_secret={os.getenv('zoho_client_secret')}&grant_type=refresh_token&client_id={os.getenv('zoho_client_id')}"
    access_token = requests.post(url)
    with open(".env_token", "w") as f:
        f.write(access_token.json()["access_token"])
    return access_token.json()["access_token"]


zoho_access_token = None


def response_handler_500(response):
    global zoho_access_token
    if response.status_code == 201:
        pass
    elif not response.status_code == 200:
        if response.json()["errors"][0]["title"] == "Invalid OAuth token.":
            zoho_access_token = generate_zoho_access_token()
            return "Make a new request"
        else:
            raise Exception(f"{response.text} {response.status_code}")
    else:
        return True


TOKEN = None


def read_token_from_env_token():
    global TOKEN
    with open(".env_token", "r") as f:
        TOKEN = f.readline()
    return TOKEN


def list_folders_zoho():
    url = "https://www.zohoapis.com/workdrive/api/v1/privatespace/p1u2g5369e6ac75d0445e9a8ab10172fc8cee/folders"

    result = "Make a new request"
    while result == "Make a new request":
        headers = {
            "Authorization": f"Zoho-oauthtoken {read_token_from_env_token()}",
        }

        response = requests.request("GET", url, headers=headers)
        result = response_handler_500(response)

    folder_lists = {}
    response_data = response.json()["data"]

    if not response_data:
        return folder_lists

    for i in range(len(response_data)):
        folder_lists[response_data[i]["attributes"]["name"]] = response_data[i][
            "id"
        ]

    return folder_lists


def create_folder_zoho(folder_lists):
    if not DIR_LIST:
        return

    url = "https://www.zohoapis.com/workdrive/api/v1/files"
    headers = {
        "Authorization": f"Zoho-oauthtoken {TOKEN}",
        "Content-Type": "application/json",
    }

    response = False
    for local_folder in DIR_LIST:
        if folder_lists == {}:
            payload = json.dumps(
                {
                    "data": {
                        "attributes": {
                            "name": f"{local_folder}",
                            "parent_id": "p1u2g5369e6ac75d0445e9a8ab10172fc8cee",
                        },
                        "type": "files",
                    }
                }
            )

            response = requests.request(
                "POST", url, headers=headers, data=payload
            )
            response_handler_500(response)
            print(f"{local_folder} created in Zoho WorkDrive")
        try:
            folder_lists[local_folder]
        except KeyError:
            payload = json.dumps(
                {
                    "data": {
                        "attributes": {
                            "name": f"{local_folder}",
                            "parent_id": "p1u2g5369e6ac75d0445e9a8ab10172fc8cee",
                        },
                        "type": "files",
                    }
                }
            )

            response = requests.request(
                "POST", url, headers=headers, data=payload
            )
            response_handler_500(response)
            print(f"{local_folder} created in Zoho WorkDrive")

    if response:
        return response.text
    else:
        return ""


def save_zoho_drive(parent_id, folder_name):
    url = f"https://www.zohoapis.com/workdrive/api/v1/upload?parent_id={parent_id}&override-name-exist=true"
    headers_for_zoho = {"Authorization": f"Zoho-oauthtoken {TOKEN}"}

    images_ext = [
        "png",
        "jpeg",
        "jpg",
        "gif",
        "PNG",
        "JPG",
        "JPEG",
        "GIF",
    ]

    for ext in images_ext:
        for local_path in Path(f"images/{folder_name}").rglob(f"*.{ext}"):
            files = {"content": open(f"{local_path}", "rb")}
            response = requests.post(url, files=files, headers=headers_for_zoho)
            response_handler_500(response)
            print(
                f"Saved {local_path} in {folder_name} in Zoho",
            )


async def download_image(url: str, images_path: str = ""):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                image_name = os.path.basename(url)
                with open(os.path.join(images_path, image_name), "wb") as f:
                    f.write(await resp.read())


def main():
    global DIR_LIST

    create_image_folder_in_local()
    DIR_LIST = os.listdir(PATH)
    add_prefix_to_local_folders()
    folder_list = list_folders_zoho()
    print(create_folder_zoho(folder_list))
    for folder_name in folder_list:
        save_zoho_drive(folder_list[folder_name], folder_name)
    client.run(os.getenv("TOKEN"))


main()
