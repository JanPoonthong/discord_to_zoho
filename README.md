# Discord To Zoho

## Requirements

### Linux / macOS / Windows

Prerequisites:

- [Python][python-download]

Instructions:

1.  Install requirement.txt:

        $ pip3 install -r requirements.txt

## About .env

Instructions:

1. Rename file `.env_sample` to `.env`
1. Add your tokens.

## How can I acquire every token?

Instructions:

1. You must follow https://discordpy.readthedocs.io/en/stable/discord.html in order to obtain `TOKEN`.

1. You must activate Discord's developer mode in order to obtain a `channel_id`.
   Enter the channel, then copy the ID (i.e artist channel).

## How can I obtain Zoho tokens?

Instructions:

1.  To register an application, go to https://workdrive.zoho.com/apidocs/v1/oauth2authentication/register-application

1.  Use this link to get to **Authorization Request**.

        https://accounts.zoho.com/oauth/v2/auth?scope=WorkDrive.files.ALL&client_id={client_id}&response_type=code&access_type=offline&redirect_uri=https://janpoonthong.github.io/portfolio/zoho&state=register

be certain to include `client_id` on `{client_id}`

1.  Copy the `code` and paste on code={}

POST request on postman:

        https://accounts.zoho.com/oauth/v2/token?code={code}&client_secret={clinet_secret}&redirect_uri=https://janpoonthong.github.io/portfolio/zoho&grant_type=authorization_code&client_id={client_id}

1.  Put that refresh token on that you will use .env
1.  Done.

[python-download]: https://www.python.org/downloads/
