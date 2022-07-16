# Self-hosting

## Prerequisites

- Python 3.8+ (as well as pip)
- Git
---
## Setup

1. Clone the repository by running `git clone https://www.github.com/trigtbh/Shebo.git`.
2. Run `pip install -r requirements.txt`.
3. [Create a bot](https://realpython.com/how-to-make-a-discord-bot-python/#how-to-make-a-discord-bot-in-the-developer-portal) through Discord's developer portal. 

    When it comes to permissions granted to the bot, the Administrator permission grants everything required to have every part of the bot running properly. 
    
    However, if you don't want to grant this permission out of caution, `414501424448` will work as a valid permissions integer (this will grant it the same permissions that standard users have).

    **Ensure that the `Presence`, `Server Members`, and `Message Content` intents are all enabled. Shebo will not work if any of these are disabled.**
---
## Configuration

Shebo operates based on settings defined in `cogs/settings.py`.
- `TOKEN`: The bot token. *This is **required***.
- `PREFIX`: The bot prefix. *This is **required***.
- `PROD_TOKEN`: If you wish to test the bot on a secondary production account, you can set that bot's token here. *This is optional.*
- `PROD_PREFIX`: Likewise, you can set the bot prefix for the secondary account here. *This is optional.*
- `LOW_DATA_MODE`: If you're running the bot on a server with limited bandwidth/less processing power (such as a Raspberry Pi on a home network), you can set this to `True` to temporarily add cooldowns to certain commands. *This is optional.*

Shebo uses a Lavalink server for music playback. If you need a Lavalink server, follow [this guide](https://www.google.com/search?q=free+lavalink+server). Its settings are also defined in `cogs/settings.py`. 

- `WL_HOST`: The Lavalink server host. *This is **required***.
- `WL_PORT`: The Lavalink server port. *This is **required***.
- `WL_REST_URI`: The REST URI for the Lavalink server. *This is **automatically configured** based on `WL_HOST` and `WL_PORT`, but if (for any reason) the REST URI for your server is different, then this is **required**.*
- `WL_PASSWORD`: The Lavalink server password. *This is **required***.

Shebo has additional features if you wish to run the bot for only one server.
- `PRIVATE_BOT`: If you wish to run the bot for only one server, set this to `True`. *This is optional.*
- `OWNER_ID`: Your Discord ID. *For the scope of this guide, this is **required***.
- `EXTRA_ANNOYING`: Adds additional, *more annoying* features to the bot. *By default, this is `False`. This only becomes **required** if `PRIVATE_BOT` is set to `True`, otherwise this is **irrelevant** and does not need to be changed.*

If `PRIVATE_BOT` is set to `True`, Shebo has additional settings that can be configured.

- `MAIN_CHANNEL`: The channel ID of the server's "general" channel (or whichever channel is most used for general chat). *This is **required** if `PRIVATE_BOT` is set to `True`. This also determines which server is considered the "main" server, as well as who is the owner of that server.*
- `EXTRA_RESPONSES`: Extra responses that can be sent by the bot to certain actions. *This is **optional**, and these responses are typically used only if `EXTRA_ANNOYING` is set to `True`.*

If `PRIVATE_BOT` is set to `True`, you have the option of having Shebo's status be set to be "Listening to", pulling songs from a given Spotify playlist. Doing this requires a [Spotify Developer account](https://developer.spotify.com/). **These settings are optional, but the status will not change unless all 3 are set.**

- `SPOTIFY_CLIENT_ID`: The Spotify client ID. *This is **semi-optional** (see above).*
- `SPOTIFY_CLIENT_SECRET`: The Spotify client secret. *This is **semi-optional** (see above).*
- `PLAYLIST_LINK`: The Spotify playlist link. *This is **semi-optional** (see above).*

Shebo has custom assets and responses that can be edited to follow a theme. These can be found in the `assets/` folder.

- `assets/ctx.json`: Help messages for all context menu commands.
- `assets/help.json`: Help messages for all commands.
- `assets/responses.json`: Responses that can be sent by the bot to certain actions.
- `assets/soundboard.json`: Soundboard entries. To add more entries, add the name of the entry as the key and the corresponding YouTube link as the value.
- `assets/words.txt`: Words that are used for the Word Guess game. If you want to use a custom wordlist, you can add those words to this file.

---
## Running

To run the bot, run `python main.py -stable`.

If you want to run the bot on a secondary testing account, run `python main.py`. Ensure that you set the `PROD_TOKEN` and `PROD_PREFIX` settings.