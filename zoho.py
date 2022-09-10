import json
import os
from pathlib import Path

import requests

import file_management

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
    url = f"https://www.zohoapis.com/workdrive/api/v1/privatespace/{os.getenv('zoho_private_space_id')}/folders"

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


def create_folder_in_zoho_request(local_folder, url, headers):
    """Request to zoho to create a folder"""
    payload = json.dumps(
        {
            "data": {
                "attributes": {
                    "name": f"{local_folder}",
                    "parent_id": f"{os.getenv('zoho_parent_id')}",
                },
                "type": "files",
            }
        }
    )

    response = requests.request("POST", url, headers=headers, data=payload)
    response_handler_500(response)
    print(f"{local_folder} created in Zoho WorkDrive")
    return response


def create_folder_zoho(folder_lists):
    """Check if folder exist in zoho, if not then create a folder"""
    if not file_management.DIR_LIST:
        return

    url = "https://www.zohoapis.com/workdrive/api/v1/files"
    headers = {
        "Authorization": f"Zoho-oauthtoken {TOKEN}",
        "Content-Type": "application/json",
    }

    response = False
    for local_folder in file_management.DIR_LIST:
        if folder_lists == {}:
            response = create_folder_in_zoho_request(local_folder, url, headers)
        try:
            folder_lists[local_folder]
        except KeyError:
            response = create_folder_in_zoho_request(local_folder, url, headers)

    if response:
        return response.text
    else:
        return ""


def save_zoho_drive(parent_id, folder_name):
    url = f"https://www.zohoapis.com/workdrive/api/v1/upload?parent_id={parent_id}&override-name-exist=true"
    headers_for_zoho = {"Authorization": f"Zoho-oauthtoken {TOKEN}"}

    for ext in file_management.image_extensions:
        for local_path in Path(f"images/{folder_name}").rglob(f"*.{ext}"):
            files = {"content": open(f"{local_path}", "rb")}
            response = requests.post(url, files=files, headers=headers_for_zoho)
            response_handler_500(response)
            print(
                f"Saved {local_path} in {folder_name} in Zoho",
            )
