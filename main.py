import os

import bot
import file_management
import zoho


def run():
    file_management.add_prefix_to_local_folders()
    # print(zoho.create_folder_zoho(bot.folder_list))
    bot.client.run(os.getenv("discord_token"))


run()
