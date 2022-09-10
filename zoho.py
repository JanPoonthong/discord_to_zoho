import json
import os
from pathlib import Path

import aiohttp
import requests

import bot
import main

TOKEN = ""


def read_token_from_env_token():
    global TOKEN
    with open(".env_token", "r") as f:
        TOKEN = f.readline()
    return TOKEN


def generate_zoho_access_token():
    url = (
        f"https://accounts.zoho.com/oauth/v2/token?refresh_token={os.getenv('zoho_refresh_token')}&"
        f"client_secret={os.getenv('zoho_client_secret')}&"
        f"grant_type=refresh_token&client_id={os.getenv('zoho_client_id')} "
    )
    access_token = requests.post(url)

    with open(".env_token", "w") as f:
        f.write(access_token.json()["access_token"])
    return access_token.json()["access_token"]


def response_handler_500(response):
    if response.status_code == 201:
        pass
    elif not response.status_code == 200:
        if response.json()["errors"][0]["title"] == "Invalid OAuth token.":
            generate_zoho_access_token()
            return "Make a new request"
        else:
            raise Exception(f"{response.text} {response.status_code}")
    else:
        return True


def list_folders_zoho():
    url = "https://www.zohoapis.com/workdrive/api/v1/privatespace/p1u2g5369e6ac75d0445e9a8ab10172fc8cee/folders"

    response = []
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
    if not main.DIR_LIST:
        return

    url = "https://www.zohoapis.com/workdrive/api/v1/files"
    headers = {
        "Authorization": f"Zoho-oauthtoken {TOKEN}",
        "Content-Type": "application/json",
    }

    response = False
    for local_folder in main.DIR_LIST:
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


def run():
    main.create_image_folder_in_local()
    main.add_prefix_to_local_folders()
    folder_list = list_folders_zoho()
    print(create_folder_zoho(folder_list))
    # for folder_name in folder_list:
    # zoho.save_zoho_drive(folder_list[folder_name], folder_name)
    bot.client.run(os.getenv("TOKEN"))


run()
