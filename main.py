import discord
from discord.ext import commands
from discord.ext import tasks


import os
import sys
import cogs.settings as settings


import random
import json

import time
import datetime

import asyncio

intents = discord.Intents.default()

intents.message_content = True
intents.presences = True
intents.members = True

here = os.path.dirname(__file__)

path = os.path.dirname(os.path.realpath(__file__))
cogs = os.path.join(path, "cogs")
sys.path.append(os.path.join(path, "cogs"))

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import cogs.settings as settings

if all([settings.SPOTIFY_CLIENT_ID, settings.SPOTIFY_CLIENT_SECRET, settings.PLAYLIST_LINK]):
    client_credentials_manager = SpotifyClientCredentials(client_id=settings.SPOTIFY_CLIENT_ID, client_secret=settings.SPOTIFY_CLIENT_SECRET)
    sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)

    playlist_URI = settings.PLAY.split("/")[-1].split("?")[0]

    tracks = []
    for t in sp.playlist_tracks(playlist_URI)["items"]:
        data = {}
        data["name"] = t["track"]["name"]
        data["artist"] = t["track"]["artists"][0]["name"]
        data["length"] = t["track"]["duration_ms"] / 1000
        tracks.append(data)

class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.remove_command("help")
        self.environment = ""

    def embed(self, title, color=None):
        if color is None:
            color = random.randint(0, 0xffffff)
        botembed = discord.Embed(title=title, color=color)

        if settings.PRIVATE_BOT:
            botembed.set_footer(text=self.response(0))
        botembed.timestamp = datetime.datetime.now()
        return botembed
       
    async def on_ready(self):
        user = self.user

        
        if len(sys.argv) > 1:
            self.environment = "stable"
        else:
            self.environment = "production"



        print("-----")
        print(f"Logged in as: {user.name}#{user.discriminator}")
        print(f"ID: {user.id}")
        cloaded = 0
        for file in os.listdir(cogs):
            if file.endswith(".py"):
                name = file[:-3]
                with open(os.path.join(cogs, file), encoding="utf-8") as f:
                    try:
                        content = f.read()
                    except:
                        print(name)
                if "# DNI" not in content:  # "DNI": Do Not Import
                    await bot.load_extension("cogs." + name, package=here)
                    cloaded += 1
        print(f"{cloaded} cogs loaded")
        print("-----")
        self.ready = True
        if all([settings.SPOTIFY_CLIENT_ID, settings.SPOTIFY_CLIENT_SECRET, settings.PLAYLIST_LINK]):
            self.update_status.start()

    def response(self, resp_type):
        options = {
            0: "footer",
            1: "accepted",
            2: "error",
            3: "join",
            4: "leave",
            5: "praise"
        }
        with open(os.path.join(path, "assets", "responses.json")) as f:
            responses = json.loads(f.read())
        
        response = random.choice(responses[options[resp_type]])
        return response

    async def on_message(self, message):
        if settings.PRIVATE_BOT:
            if message.guild:
                channel = self.bot.get_channel(settings.MAIN_CHANNEL)
                guild = channel.guild
                if message.guild.id != guild.id: return
            else: return
        else: 
            if message.guild:
                if message.type == discord.MessageType.new_member:
                    embed = self.embed("Welcome", color=0xF4EA56)
                    embed.description = f"👋 Welcome <@{message.author.id}> to the server! We hope you enjoy your stay!"

                    gifs = [
                        "https://cdn.discordapp.com/attachments/696824828258156615/988857015373824080/Wave.gif",
                        "https://cdn.discordapp.com/attachments/696824828258156615/988857046944317510/Scream.gif",
                        "https://cdn.discordapp.com/attachments/696824828258156615/988857060475142184/Wave.gif",
                        "https://cdn.discordapp.com/attachments/696824828258156615/988857083623534643/Sup.gif",
                        "https://cdn.discordapp.com/attachments/696824828258156615/988857092586766386/Wave.gif",
                        "https://cdn.discordapp.com/attachments/696824828258156615/988857100669190234/Wave.gif"

                    ]
                    embed.set_image(url=random.choice(gifs))
                    return await message.reply(embed=embed)
            else: return
        await self.process_commands(message)

    @tasks.loop()
    async def update_status(self):
        random.shuffle(tracks)
        for t in tracks:
            await self.change_presence(activity=discord.Activity(
                name=f"{t['artist']} - {t['name']}", 
                type=discord.ActivityType.listening, 
                timestamps={"start": time.time() * 1000, "end": (time.time() + t["length"]) * 1000}
                
                ))
            await asyncio.sleep(t["length"])

        
p = (settings.PREFIX if len(sys.argv) != 1 else settings.PROD_PREFIX)
bot = Bot(command_prefix=p, activity=discord.Game(name=f"{p}help for help"), intents=intents)
bot.remove_command("help")

async def main():
    async with bot:
        if len(sys.argv) > 1:
            t = settings.TOKEN
        else:
            t = settings.PROD_TOKEN
        await bot.start(t)

if __name__ == "__main__":
    asyncio.run(main())