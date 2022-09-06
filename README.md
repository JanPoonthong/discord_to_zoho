# Discord To Zoho

## Requirements

### Linux / macOS / Windows

Prerequisites:

- [Python][python-download]

Instructions:

1.  Install requirement.txt:

        $ pip3 install -r requirements.txt

## Create .env

Instructions:

1. Rename file `.env_sample` to `.env`
1. Add your tokens.

## How to get all tokens?

Instructions:

1. To get `TOKEN`, you need to follow https://discordpy.readthedocs.io/en/stable/discord.html
1. To get `channel id`, you need to turn on your developer mode in Discord. Go the channel and copy the id(i.e artist channel).

## How to get Zoho tokens?

Instructions:

1.  Follow these step: https://workdrive.zoho.com/apidocs/v1/oauth2authentication/register-application
1.  When you reach **Authorization Request** use this link

        https://accounts.zoho.com/oauth/v2/auth?scope=WorkDrive.files.ALL&client_id={client_id}&response_type=code&access_type=offline&redirect_uri=https://janpoonthong.github.io/portfolio/zoho&state=register

make sure you add your `client_id` on `{client_id}`

1.  Copy the code and paste on code={}

        https://accounts.zoho.com/oauth/v2/token?code={code}&client_secret={clinet_secret}&redirect_uri=https://janpoonthong.github.io/portfolio/zoho&grant_type=authorization_code&client_id={client_id}

1.  You will refresh_token, put that refresh_token on .env
1.  Done.

[python-download]: https://www.python.org/downloads/
