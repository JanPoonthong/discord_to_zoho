import os

import bot
import file_management


def run():
    file_management.add_prefix_to_local_folders()
    bot.client.run(os.getenv("discord_token"))


run()
