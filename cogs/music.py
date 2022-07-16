
# Standard music cog. If this is failing, DNI this file and switch to music2.py

import asyncio
import discord
import re
import sys
import traceback
import wavelink
from discord.ext import commands
from typing import Union
import functions
from youtube_search import YoutubeSearch as ys
import random
import time
import settings
import os
import json
from gtts import gTTS

path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

def generate_code():
    chars = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890"
    code = ""
    for _ in range(15):
        code = code + random.choice(chars)
    return code

def slice_n(lst, n):
    for i in range(0, len(lst), n): 
        yield lst[i:i + n] 

RURL = re.compile('https?:\/\/(?:www\.)?.+')

def botembed(title):
    embed = functions.embed("Music - " + title, color=0x8f0000)
    return embed

def error(errormsg):
    embed = functions.error("Music", errormsg)
    return embed
    

class MusicController:

    def __init__(self, bot, node, guild):
        self.bot = bot
        self.node = node
        self.guild = guild
        self.channel = None

        self.next = asyncio.Event()
        self.queue = asyncio.Queue()
        self.links = asyncio.Queue()

        self.volume = 100
        self.now_playing = None

        self.looping = False
        self.start = time.time()

        self.silent = False
        self.first_time = False

        self.timestamps = asyncio.Queue()

        self.true_voice = None

        self.bot.loop.create_task(self.controller_loop())
        

    async def controller_loop(self):
        
        player = self.node.get_player(self.guild)
        await player.set_volume(self.volume)

        while True:
            self.playing = False
            if not self.looping:
                self.first_time = True
            self.next.clear()
            if not self.looping:
                self.song = await self.queue.get()
                self.link = await self.links.get()
            await player.play(self.song)

            
            self.timestamps = asyncio.Queue()
            await self.timestamps.put(time.time())
            

            
            if not self.silent:
                if not self.looping:
                    embed = botembed("Now Playing")
                    embed.description = f"🎵 " + self.bot.response(3) + f" [{self.song}]({self.link}) is now playing!"
                    self.now_playing = await self.channel.send(embed=embed)
                    self.first_time = True
                elif self.first_time:
                    embed = botembed("Now Playing")
                    embed.description = f"🎵 " + self.bot.response(3) + f" [{self.song}]({self.link}) is now playing!"
                    self.now_playing = await self.channel.send(embed=embed)
                    self.first_time = False
            self.playing = True
            self.silent = False
            await self.next.wait()


class Music(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.controllers = {}

        #if not hasattr(bot, 'wavelink'):
        #    self.node = wavelink.Client(bot=self.bot)

        
        self.bot.loop.create_task(self.start_nodes())

    async def start_nodes(self):
        await self.bot.wait_until_ready()

        # Initiate our nodes. For this example we will use one server.
        # Region should be a discord.py guild.region e.g sydney or us_central (Though this is not technically required)

        self.node = await wavelink.NodePool.create_node(bot=self.bot,
                                            host=settings.WL_HOST,
                                            port=settings.WL_PORT,
                                            password=settings.WL_PASSWORD
        )

        self.bot.music_loaded = True

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player, track, reason):
        """Node hook callback"""
        controller = self.get_controller(player)
        controller.next.set()

    def get_controller(self, value: Union[commands.Context, wavelink.Player]):
        gid = value.guild

        try:
            controller = self.controllers[gid.id]
        except KeyError:
            controller = MusicController(self.bot, self.node, gid)
            self.controllers[gid.id] = controller

        return controller

    async def cog_check(self, ctx):
        """A local check which applies to all commands in this cog"""
        if not ctx.guild:
            raise commands.NoPrivateMessage
        return True

    async def cog_command_error(self, ctx, error):
        """A local error handler for all errors arising from commands in this cog"""
        if isinstance(error, commands.NoPrivateMessage):
            try:
                embed = error("🚫 " + self.bot.response(2) + " this command can't be used in DMs.")
                return await ctx.send(embed=embed)
            except discord.HTTPException:
                pass

        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    @commands.command(name='connect', aliases=["join"])
    async def connect_(self, ctx, *, channel: discord.VoiceChannel=None, silent=False):
        """Connect to a valid voice channel"""
        if not channel:
            try:
                channel = ctx.author.voice.channel
            except AttributeError:
                raise discord.DiscordException('No channel to join. Please either specify a valid channel or join one.')
        
        controller = self.get_controller(ctx)
        controller.channel = ctx.channel
        controller.true_voice = channel

        await channel.connect(cls=wavelink.Player)
        try:
            player = self.node.get_player(ctx.guild)
        except wavelink.errors.ZeroConnectedNodes:
            await self.start_nodes()
            player = self.node.get_player(ctx.guild)
         
        if not silent:
            embed = botembed("Connected")
            embed.description = "🔊 " + self.bot.response(3) + f" I've connected to `{channel.name}`."
            await ctx.send(embed=embed)


        
    @commands.command(aliases=["p"])
    async def play(self, ctx, *, query: str=None, silent=False, bypass=False):
        """Search for and add a song to the queue"""
        
        player = self.node.get_player(ctx.guild)
        if not player:
            await ctx.invoke(self.connect_, silent=silent)
        elif not player.is_connected():
            await ctx.invoke(self.connect_, silent=silent)
            

        if not query:
            embed = error("🚫 " + self.bot.response(2) + " you need to pass a search term or link to play a song.")
            return await ctx.send(embed=embed)

        #await self.start_nodes()
        qcopy = query
        controller = self.get_controller(ctx)
        if not RURL.match(query) and not bypass:
            query = f'ytsearch:{query}'
            
            search_results = ys(query, max_results=1).to_dict()
            href = search_results[0]["url_suffix"]

            base = ("https://www.youtube.com" + href)
            query = base

            
        await controller.links.put(query)
        
        if not bypass:
            try:    
                tracks = await self.node.get_tracks(wavelink.YouTubeTrack, query)
            except wavelink.errors.ZeroConnectedNodes:
                await self.start_nodes()
                tracks = await self.node.get_tracks(wavelink.YouTubeTrack, query)
        else:
            tracks = list(await self.node.get_tracks(query=query, cls=wavelink.Track))

        if not tracks:
            embed = error("🚫 " + self.bot.response(2) + " it looks like I couldn't find anything with that query.")
            return await ctx.send(embed=embed)

        

        track = tracks[0]

        controller = self.get_controller(ctx)
        controller.silent = silent
        send = False
        if len(controller.queue._queue) > 0:
            send = True
        elif player:
            if controller.playing:
                send = True
        if send:
            embed = botembed("Song Added")
            await controller.links.put(query)
            embed.description = ("📥 " + self.bot.response(1) +  f" `{str(track)}` has been added to the queue.")
            await ctx.send(embed=embed)
        else:
            controller.first_time = True
        await controller.queue.put(track)

    @commands.command()
    async def pause(self, ctx):
        """Pause the player"""
        player = self.node.get_player(ctx.guild)
        controller = self.controllers.get(ctx.guild.id)
        if not player.is_playing:
            embed = error("🚫 " + self.bot.response(2) +  " it looks like I'm not playing anything right now...")
            return await ctx.send(embed=embed)

        embed = botembed("Paused")
        await player.set_pause(True)
        await controller.timestamps.put(time.time())
        embed.description = "⏸️ " + self.bot.response(1) + " I've paused the current song."
        await ctx.send(embed=embed)
        

    @commands.command(aliases=["res"])
    async def resume(self, ctx):
        """Resume the player from a paused state"""
        player = self.node.get_player(ctx.guild)
        controller = self.controllers.get(ctx.guild.id)
        if not player.is_paused:
            embed = error("🚫 " + self.bot.response(2) +  " it looks like I'm not paused right now...")
            return await ctx.send(embed=embed)

        await player.set_pause(False)
        await controller.timestamps.put(time.time())
        embed = botembed("Resumed")
        embed.description = "▶️ " + self.bot.response(1) + " I've resumed the current song."
        await ctx.send(embed=embed)
        

    @commands.command(aliases=["s"])
    async def skip(self, ctx, silent=False):
        """Skip the currently playing song"""
        player = self.node.get_player(ctx.guild)

        if not player.is_playing:
            if silent:
                raise IndexError("nothing in queue")
            embed = error("🚫 " + self.bot.response(2) +  " it looks like I'm not playing anything right now...")
            return await ctx.send(embed=embed)

        #await ctx.send('Skipping the song!', delete_after=15)
        if silent:
            player.silent = True
        controller = self.get_controller(player)
        if controller.looping:
            controller.looping = False
        if len(controller.queue._queue) > 0:
            controller.next.set()
        else:
            
            await player.stop()

    @commands.command(aliases=["vol"])
    async def volume(self, ctx, *, vol=None):
        """Set the player volume"""
        player = self.node.get_player(ctx.guild)
        controller = self.get_controller(ctx)
        if not vol:
            embed = botembed("Current volume")
            embed.description = "🔊 " + self.bot.response(3) + f" The volume is currently set to `{controller.volume}/100`."
            return await ctx.send(embed=embed)
        elif not(vol.isdigit()):
            embed = error("🚫 " + self.bot.response(2) + " you need to pass a volume setting between 0 and 100.")
            return await ctx.send(embed=embed)
        
        player = self.node.get_player(ctx.guild)
        controller = self.get_controller(ctx)
        vol = int(vol)
        vol = max(min(vol, 100), 0)
        controller.volume = vol

        
        embed = botembed("Volume Set")
        embed.description = "🔊 " + self.bot.response(1) + f" I set the volume to `{vol}/100`."
        await ctx.send(embed=embed)
        await player.set_volume(vol)

    @commands.command(aliases=['np', 'current', 'nowplaying'])
    async def now_playing(self, ctx):
        """Retrieve the currently playing song"""
        player = self.node.get_player(ctx.guild)

        if not player.track:
            embed = error("🚫 " + self.bot.response(2) +  " it looks like I'm not playing anything right now...")
            return await ctx.send(embed=embed)


        controller = self.get_controller(ctx)
        #await controller.now_playing.delete()

        temp = list(controller.timestamps._queue.copy())
        if len(temp) % 2 == 1:
            temp.append(time.time())

        chunked = list(slice_n(temp, 2))
        total = sum([x[1] - x[0] for x in chunked])
        
        length = time.gmtime(controller.song.length)
        if controller.song.length >= 3600:
            fstring = "%H:%M:%S"
        else:
            fstring = "%M:%S"
        length_r = time.strftime(fstring, length)

        dt = time.gmtime(total)
        dt_r = time.strftime(fstring, dt)

        
        embed = botembed("Now Playing")

        embed.description = ("🔊 " + self.bot.response(1) + f" Currently, I'm playing [{controller.song}]({controller.link})\n(`{dt_r}` / `{length_r}`).")

        controller.now_playing = await ctx.send(embed=embed)

    @commands.command(aliases=['q'])
    async def queue(self, ctx, page=1):
        """Retrieve information on the next 5 songs from the queue"""
        
        controller = self.get_controller(ctx)
        
        if not(str(page).isdigit()):
            embed = error("🚫 " + self.bot.response(2) +  " you need to pass a page number to view.")
            return await ctx.send(embed=embed)
        page = int(page)

        viewable = 5

        pages = int(len(controller.queue._queue) // viewable) + (1 if len(controller.queue._queue) % viewable > 0 else 0)

        page = min(max(page, 1), pages)
        start = (page-1) * viewable
        end = min(max(start + viewable, 1), len(controller.queue._queue))


        player = self.node.get_player(ctx.guild)
        if not player.track or not controller.queue._queue:
            embed = error("🚫 " + self.bot.response(2) +  " there's nothing in the queue right now...")
            return await ctx.send(embed=embed)

        upcoming = list(controller.queue._queue)[start:end]
        upcominglinks = list(controller.links._queue)[start:end]

        desc = ""
        for i in range(len(upcoming)):
            desc = desc + f"\n**{start + i + 1}**: [{upcoming[i]}]({upcominglinks[i]})" 

        embed = botembed(f"Queue (#{start + 1} - #{end})")

        embed.description = "🔢 " + self.bot.response(1) + f" Here's what's next...\n(Showing page {page} of {pages})\n" + desc

        await ctx.send(embed=embed)

    @commands.command(aliases=['disconnect', 'dc', "dis", "leave"])
    async def stop(self, ctx):
        """Stop and disconnect the player and controller"""
        player = self.node.get_player(ctx.guild)
        smember = ctx.guild.get_member(self.bot.user.id)
        if not smember.voice:
            embed = error("🚫 " + self.bot.response(2) + " I'm not connected to a voice channel right now...")
            return await ctx.send(embed=embed)
        channel = smember.voice.channel
        controller = self.get_controller(ctx)
        for _ in range(len(controller.queue._queue)):
            await self.skip(ctx, silent=True)

        try:
            del self.controllers[ctx.guild.id]
        except KeyError as e:
            await player.disconnect(force=True)
            print("f", str(e))
            embed = botembed("Disconnected")
            embed.description = "👋 " + self.bot.response(4) + f" I've disconnected from `{channel.name}`."
            return await ctx.send(embed=embed)


        #player = self.node.get_player(ctx.guild)
        player.next = asyncio.Event()
        player.queue = asyncio.Queue()
        player.links = asyncio.Queue()
        
        player.now_playing = None
        await player.stop()

        await player.disconnect(force=True)
        del player


        

        embed = botembed("Disconnected")
        embed.description = "👋 " + self.bot.response(4) + f" I've disconnected from `{channel.name}`."
        await ctx.send(embed=embed)

        
    @commands.command()
    async def move(self, ctx, frompos=None, topos=None):
        """Move a song from one position in the queue to another"""
        if not topos:
            embed = error("🚫 " + self.bot.response(2) +  " you need to specify where you want your song to go.")
            return await ctx.send(embed=embed)
        if not(frompos.isdigit()) or not(topos.isdigit()):
            embed = error("🚫 " + self.bot.response(2) +  " you need to specify where in the queue you want your song to go.")
            return await ctx.send(embed=embed)
        
        controller = self.get_controller(ctx)
        player = self.node.get_player(ctx.guild)
        if not player.track or not controller.queue._queue:
            embed = error("🚫 " + self.bot.response(2) +  " there's nothing in the queue right now...")
            return await ctx.send(embed=embed)


        frompos = min(max(int(frompos), 1), len(controller.queue._queue))
        topos = min(max(int(topos), 1), len(controller.queue._queue))
        frompos -= 1
        topos -= 1
        
        song = controller.queue._queue[frompos]
        link = controller.links._queue[frompos]


        del controller.queue._queue[frompos]
        del controller.links._queue[frompos]


        controller.queue._queue.insert(topos, song)
        controller.links._queue.insert(topos, link)

        

        embed = botembed("Song Moved")
        embed.description = "🔄 " + self.bot.response(1) +  " [{}]({}) has been moved from `#{}` to `#{}` in the queue.".format(song, link, frompos + 1, topos + 1)
        return await ctx.send(embed=embed)

    @commands.command(aliases=["r"])
    async def remove(self, ctx, pos=None):
        if not pos:
            embed = error("🚫 " + self.bot.response(2) +  " you need to specify what song you want to remove.")
            return await ctx.send(embed=embed)
        if not(pos.isdigit()):
            embed = error("🚫 " + self.bot.response(2) +  " you need to specify what song in the queue you want to remove.")
            return await ctx.send(embed=embed)

        
        
        controller = self.get_controller(ctx)
        player = self.node.get_player(ctx.guild)
        if not player.track or not controller.queue._queue:
            embed = error("🚫 " + self.bot.response(2) +  " there's nothing in the queue right now...")
            return await ctx.send(embed=embed)

        pos = min(max(int(pos), 1), len(controller.queue._queue))

        pos -= 1

        song = controller.queue._queue[pos]
        link = controller.links._queue[pos]

        del controller.queue._queue[pos] 
        del controller.links._queue[pos]

        embed = botembed("Song Removed")
        embed.description = "📤 " + self.bot.response(1) +  " [{}]({}) has been removed from the queue.".format(song, link)
        return await ctx.send(embed=embed)


    @commands.command()
    async def loop(self, ctx):
        """Loops the currently playing song"""
        player = self.node.get_player(ctx.guild)
        if not player:
            embed = error("🚫 " + self.bot.response(2) +  " I'm not connected to a voice channel right now...")
            return await ctx.send(embed=embed)
        

        controller = self.get_controller(ctx)
        

        
        controller.looping = not(controller.looping)
        if controller.looping:
            if player:
                if player.is_playing():
                    controller.first_time = False

        embed = botembed("Loop Toggled")
        embed.description = "🔁 " + self.bot.response(1) +  " Looping has been `turned {}`.".format("on" if controller.looping else "off")
        return await ctx.send(embed=embed)
        
    @commands.command(aliases=["sb"])
    async def soundboard(self, ctx, query=None):
        
        if not query:
            embed = error("🚫 " + self.bot.response(2) +  " you need to specify a sound to play.")
            return await ctx.send(embed=embed)
        
        query = query.lower().strip()

        with open(os.path.join(path, "assets", "soundboard.json")) as f:
            board = json.loads(f.read())

        if query not in board.keys():
            embed = error("🚫 " + self.bot.response(2) +  f" I couldn't find a sound named `{query}`.")
            return await ctx.send(embed=embed)

        player = self.node.get_player(ctx.guild)
        if player:
            controller = self.get_controller(ctx)
            if controller:
                try:
                    if not controller.queue.empty() or controller.playing:
                        embed = error("🚫 " + self.bot.response(2) +  f" the soundboard cannot be used while music is playing or queued.")
                        return await ctx.send(embed=embed)
                except:
                    pass

        await ctx.message.add_reaction("🎶")

        await ctx.invoke(self.play, query=board[query], silent=True, bypass=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Music(bot))
