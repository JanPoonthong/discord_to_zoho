import json
import os

import requests

import file_management


TOKEN = ""


def read_token_from_env_token():
    global TOKEN
    with open(".env_token", "r") as f:
        TOKEN = f.readline()
    return TOKEN


def generate_zoho_access_token():
    print("Generating zoho token")
    url = (
        f"https://accounts.zoho.com/oauth/v2/token?refresh_token={os.getenv('zoho_refresh_token')}&"
        f"client_secret={os.getenv('zoho_client_secret')}&"
        f"grant_type=refresh_token&client_id={os.getenv('zoho_client_id')} "
    )
    access_token = requests.post(url)

    print("Saving zoho token")
    with open(".env_token", "w") as f:
        f.write(access_token.json()["access_token"])
    return access_token.json()["access_token"]


# Regenerated expired access token or raise an exception
def error_handler(response):
    if response.status_code == 201:
        pass
    elif not response.status_code == 200:
        print(response.text)
        print(f"Error {response.status_code}")
        if response.json()["errors"][0]["title"] == "Invalid OAuth token.":
            generate_zoho_access_token()
            return "Make a new request"
        else:
            raise Exception(f"{response.text} {response.status_code}")
    else:
        return True


def list_folders_zoho():
    print("listing zoho folders")
    url = f"https://www.zohoapis.com/workdrive/api/v1/privatespace/{os.getenv('zoho_private_space_id')}/folders"

    response = None
    result = "Make a new request"
    while result == "Make a new request":
        headers = {
            "Authorization": f"Zoho-oauthtoken {read_token_from_env_token()}",
        }
        response = requests.request("GET", url, headers=headers)
        result = error_handler(response)

    folder_lists = {}
    response_data = response.json()["data"]

    if not response_data:
        print("No folders found")
        return folder_lists

    print(f"Found {len(response_data)} folders")
    for i in range(len(response_data)):
        folder_lists[response_data[i]["attributes"]["name"]] = response_data[i][
            "id"
        ]

    return folder_lists


def create_folder_in_zoho_request(local_folder, url, headers):
    """Request to zoho to create a folder"""
    print("Creating folder in zoho")
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
    error_handler(response)
    print(f"{local_folder} created in Zoho WorkDrive")
    return response


# Check if folder exist in zoho, if not then create a folder
def create_folder_zoho(folder_lists):
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


# make changes
def save_zoho_drive(author_name, file_name):
    folders_list = list_folders_zoho()
    print(author_name)
    print(folders_list)
    if author_name not in folders_list:
        create_folder_in_zoho_request(
            author_name,
            "https://www.zohoapis.com/workdrive/api/v1/files",
            {
                "Authorization": f"Zoho-oauthtoken {TOKEN}",
                "Content-Type": "application/json",
            },
        )
        folders_list = list_folders_zoho()
    parent_id = folders_list[author_name]

    print(folders_list)

    print(f"Saving {file_name} on zoho")
    url = f"https://www.zohoapis.com/workdrive/api/v1/upload?parent_id={parent_id}&override-name-exist=true"
    headers_for_zoho = {"Authorization": f"Zoho-oauthtoken {TOKEN}"}

    files = {"content": open(f"/tmp/{file_name}", "rb")}
    response = requests.post(url, files=files, headers=headers_for_zoho)
    error_handler(response)
    print(
        f"Saved {file_name} in {author_name} in Zoho",
    )
