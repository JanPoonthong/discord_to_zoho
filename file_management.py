import os

from dotenv import load_dotenv

load_dotenv()
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
PATH = "images/"

# This is images/ folder where all the user folder would be inside.
if not os.path.exists(PATH):
    os.mkdir(PATH)

DIR_LIST = os.listdir(PATH)
CURRENT_DIRECTORY = os.getcwd()
TOKEN = None


def add_prefix_to_local_folders():
    """Add a user_ as a prefix to username of Discord user."""
    for folder in DIR_LIST:
        if folder.startswith("user_"):
            continue
        else:
            DIR_LIST.remove(folder)


async def save_image_on_local(messages):
    files_completed = []

    for message in messages:
        for attachment in message.attachments:
            final_directory = os.path.join(
                CURRENT_DIRECTORY + f"/{PATH}", f"user_{message.author}"
            )
            if not os.path.exists(final_directory):
                os.makedirs(final_directory)
            author_images = os.listdir(final_directory)
            for image in author_images:
                files_completed.append(image.removeprefix("file_"))
            if attachment.filename in files_completed:
                continue
            if valid_image_url(attachment.url):
                await attachment.save(
                    os.path.join(
                        final_directory, "file_" + attachment.filename,
                    )
                )


def valid_image_url(url: str):
    for image_extension in image_extensions:
        if url.endswith("." + image_extension):
            return True
    return False
