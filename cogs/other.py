import discord
import os
import json
import settings
from discord.ext import commands
import functions
import traceback

path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

class Other(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, e):
        if isinstance(e, commands.CommandOnCooldown):
            embed = functions.error("Cooldown", "⏱️ " + self.bot.response(2) + f" this command is temporarily on cooldown!\nThe command can be used {e.cooldown.rate} time{'' if e.cooldown.rate == 1 else 's'} every {int(e.cooldown.per)} second{'' if int(e.cooldown.per) == 1 else 's'}.\nYou can use it again in `{int(round(e.retry_after))} second{'' if int(round(e.retry_after)) == 1 else 's'}`.")
            return await ctx.send(embed=embed)
        else:
            try:
                raise e # stimulate error so it gets entered into traceback
            except:
                owner = self.bot.get_user(settings.OWNER_ID)
                tb = traceback.format_exc()
                if len(tb) > 4096:
                    tb = tb[:4093] + "..."
                embed = functions.error("Command Error", f"Message: [Jump!]({ctx.message.jump_url})\n```{tb}```")
                await owner.send(embed=embed)

    @commands.command()
    async def help(self, ctx, command=None):
        with open(os.path.join(path, "assets", "help.json")) as f:
            commandhelp = json.loads(f.read())
        description = f"Command prefix: `{settings.PREFIX}`\nRequired parameters: **<**parameter**>**\nOptional parameters: **[**parameter**]**\nUse `{settings.PREFIX}ctx` for help with context menu commands"

        if command is None:
            embed = functions.embed("Help", color=0x4b5aff)
            embed.description = description
            for key in commandhelp.keys():
                embed.add_field(name=key, value=", ".join([k.split(" ")[0] for k in commandhelp[key].keys()]), inline=False)
        elif command.lower() in [k.lower() for k in commandhelp.keys()]:
            embed = functions.embed("Help - " + command.title(), color=0x4b5aff)
            embed.description = description
            embed.add_field(name="Commands", value=", ".join([k.split(" ")[0] for k in commandhelp[command.title()].keys()]))
        elif command.lower() in [v.split(" ")[0] for k in commandhelp.keys() for v in commandhelp[k].keys()]:
            command = command.lower()
            group = [k for k in commandhelp.keys() if command in commandhelp[k].keys()][0]

            embed = functions.embed("Help - " + command, color=0x4b5aff)

            if command != "soundboard":
                embed.description = description + "\n\n" + commandhelp[group][command][1]
            else:
                with open(os.path.join(path, "assets", "soundboard.json")) as f:
                    board = json.loads(f.read())
                embed.description = description + "\n\n" + "Plays a sound given an input string.\nAvailable sounds:\n`" + "  ".join(sorted(board.keys())) + "`"

            
            
            embed.add_field(name="Usage", value=f"{settings.PREFIX}{command} {commandhelp[group][command][0]}", inline=False)
        else:
            embed = functions.error("Help", "🚫 " + self.bot.response(2) + f" I couldn't find a command/group called `{command}`.")
        await ctx.send(embed=embed)

    @commands.command(name="ctx")
    async def context(self, ctx, command=None):
        with open(os.path.join(path, "assets", "ctx.json")) as f:
            ctxhelp = json.loads(f.read())
        description = "Context commands are available by right-clicking/selecting a message"
        if command is None:
            embed = functions.embed("Help (Context Commands)", color=0x4b5aff)
            embed.add_field(name="Available Commands", value=", ".join([c for c in ctxhelp.keys()]))
            embed.description = description
        elif command not in [k.lower() for k in ctxhelp.keys()] + [k.upper() for k in ctxhelp.keys()] + [k.title() for k in ctxhelp.keys()]:
            embed = functions.error("Help (Context Commands)", "🚫 " + self.bot.response(2) + f" I couldn't find a context command called `{command}`.")
        else:
            name = [k for k in ctxhelp.keys() if command in (k.lower(), k.upper(), k.title())][0]
            embed = functions.embed("Help (Context Commands) - " + name, color=0x4b5aff)
            description = description + f"\n\n**{name}**: {ctxhelp[name]}"
            embed.description = description
        await ctx.send(embed=embed)

    @commands.command()
    async def ping(self, ctx):
        embed = functions.embed("Ping", color=0x4b5aff)
        embed.description = f"🏓 Pong! Response time: `{round(self.bot.latency * 1000, 3)} ms`"
        if settings.LOW_DATA_MODE:
            embed.description = embed.description + "\n*The bot is currently on low data mode, which may result in higher response times*"
        return await ctx.send(embed=embed)

    

async def setup(bot):
    await bot.add_cog(Other(bot))