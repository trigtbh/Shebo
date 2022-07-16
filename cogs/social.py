from discord.ext import commands
import discord
import functions
import random
import settings
import asyncio
import datetime
import time
from discord.ext import tasks

def error(errormsg):
    embed = functions.error("Social", errormsg)
    return embed

class Social(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        if self.PRIVATE_BOT:
            c = self.bot.get_channel(settings.MAIN_CHANNEL)
            guild = c.guild
            self.server_owner = guild.owner.id
        
        self.check_online.start()

    async def cog_before_invoke(self, ctx: commands.Context):
        if ctx.author.id == settings.OWNER_ID:
            return ctx.command.reset_cooldown(ctx)

    @commands.Cog.listener()
    async def on_presence_update(self, before, after):
        if settings.PRIVATE_BOT and settings.EXTRA_ANNOYING:
            if before.id == self.server_owner:
                now = time.localtime()
                h = now.tm_hour
                if h > 21 or h < 6:
                    if before.status == discord.Status.offline and after.status != discord.Status.offline:
                         c = self.bot.get_channel(settings.MAIN_CHANNEL)
                         await c.send(f"<@{before.id}> go to sleep")

    @tasks.loop()
    async def check_online(self, *args):
        if settings.PRIVATE_BOT and settings.EXTRA_ANNOYING:
            now = time.localtime()
            h, m, s = now.tm_hour, now.tm_minute, now.tm_second
            totals = (h * 3600) + (m * 60) + s
            targets = 21 * 3600
            

            distance = targets - totals
            if distance < 0:
                distance += (24 * 3600)
            elif distance == 0:
                return
            await asyncio.sleep(distance)
            c = self.bot.get_channel(settings.MAIN_CHANNEL)
            guild = c.guild
            
            m = guild.get_member(self.server_owner)
            if m.status != discord.Status.offline:
                await c.send(f"<@{m.id}> go to sleep")

    @commands.Cog.listener()
    async def on_message(self, message):
        if self.bot.user in message.mentions:
            random.seed(message.author.id)
            lat = round(random.random() * 1000 % 180, 4)
            lon = round(random.random() * 1000 % 360, 4)
            
            if lat > 90:
                slat = str(180 - lat) + "°S"
            else:
                slat = str(lat) + "°N"

            if lon > 180:
                slon = str(360 - lon) + "°E"
            else:
                slon = str(lon) + "°W"

            random.seed(message.author.id)
            responses = ["No u", "L", "Ratio", "Ok", "Bad", f"/ban <@{message.author.id}>", "1v1 me", f"10.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)} :)", f"172.{random.randint(16, 31)}.{random.randint(0, 255)}.{random.randint(0, 255)} :)", f"192.168.{random.randint(0, 255)}.{random.randint(0, 255)} :)", "Cringe", "Don't care", "Didn't ask", f"{slat}, {slon} :)"]
            if settings.PRIVATE_BOT:
                responses = responses + settings.EXTRA_RESPONSES
            random.seed()
            await message.reply(random.choice(responses))


    @commands.cooldown(1, 0 if not settings.LOW_DATA_MODE else 10, commands.BucketType.user)
    @commands.command()
    async def slap(self, ctx, check: str = None):
        if check is None:
            embed = functions.error("Slap", "🚫 " + self.bot.response(2) + f" it looks like you need to specify a user.")
            return await ctx.send(embed=embed)
        try:
            member = await commands.MemberConverter().convert(ctx, check)
        except Exception as e:
            embed = functions.error("Slap", "🚫 " + self.bot.response(2) + f" I couldn't find a user named `{check}`.")
            return await ctx.send(embed=embed)
        embed = functions.embed("Slap", color=0xeb7d34)
        embed.description = f"Ouch! <@{ctx.author.id}> slapped <@{member.id}>."

        gifs = [
            "https://c.tenor.com/EzwsHlQgUo0AAAAC/slap-in-the-face-angry.gif",
            "https://c.tenor.com/ImQ3_wc8sF0AAAAM/ru-paul-slap.gif",
            "https://c.tenor.com/yJmrNruFNtEAAAAC/slap.gif",
            "https://c.tenor.com/R-fs21xH13QAAAAM/slap-kassandra-lee.gif"

        ]

        embed.set_image(url=random.choice(gifs))
        return await ctx.send(embed=embed)

    @commands.cooldown(1, 0 if not settings.LOW_DATA_MODE else 10, commands.BucketType.user)
    @commands.command()
    async def kiss(self, ctx, check: str = None):
        if check is None:
            embed = functions.error("Kiss", "🚫 " + self.bot.response(2) + f" it looks like you need to specify a user.")
            return await ctx.send(embed=embed)
        try:
            member = await commands.MemberConverter().convert(ctx, check)
        except Exception as e:
            embed = functions.error("Kiss", "🚫 " + self.bot.response(2) + f" I couldn't find a user named `{check}`.")
            return await ctx.send(embed=embed)
        embed = functions.embed("Kiss", color=0xeb7d34)
        embed.description = f"Awww, <@{ctx.author.id}> kissed <@{member.id}>."

        gifs = [
            "https://c.tenor.com/gUiu1zyxfzYAAAAi/bear-kiss-bear-kisses.gif",
            "https://c.tenor.com/zFzhOAJ8rqwAAAAC/love.gif"

        ]

        embed.set_image(url=random.choice(gifs))
        return await ctx.send(embed=embed)
        
    @commands.cooldown(1, 0 if not settings.LOW_DATA_MODE else 10, commands.BucketType.user)
    @commands.command()
    async def punch(self, ctx, check: str = None):
        if check is None:
            embed = functions.error("Punch", "🚫 " + self.bot.response(2) + f" it looks like you need to specify a user.")
            return await ctx.send(embed=embed)
        try:
            member = await commands.MemberConverter().convert(ctx, check)
        except Exception as e:
            embed = functions.error("Punch", "🚫 " + self.bot.response(2) + f" I couldn't find a user named `{check}`.")
            return await ctx.send(embed=embed)
        embed = functions.embed("Punch", color=0xeb7d34)
        embed.description = f"Ouch! <@{ctx.author.id}> punched <@{member.id}>."

        gifs = [
            "https://c.tenor.com/5iVv64OjO28AAAAC/milk-and-mocha-bear-couple.gif",
            "https://c.tenor.com/UAG36LOiVDwAAAAC/milk-and-mocha-happy.gif"

        ]

        embed.set_image(url=random.choice(gifs))
        return await ctx.send(embed=embed)

    @commands.cooldown(1, 0 if not settings.LOW_DATA_MODE else 10, commands.BucketType.user)
    @commands.command()
    async def hug(self, ctx, check: str = None):
        if check is None:
            embed = functions.error("Hug", "🚫 " + self.bot.response(2) + f" it looks like you need to specify a user.")
            return await ctx.send(embed=embed)
        try:
            member = await commands.MemberConverter().convert(ctx, check)
        except Exception as e:
            embed = functions.error("Hug", "🚫 " + self.bot.response(2) + f" I couldn't find a user named `{check}`.")
            return await ctx.send(embed=embed)
        embed = functions.embed("Hug", color=0xeb7d34)
        embed.description = f"Awww, <@{ctx.author.id}> hugged <@{member.id}>."

        gifs = [
            "https://c.tenor.com/OXCV_qL-V60AAAAM/mochi-peachcat-mochi.gif",
            "https://c.tenor.com/jU9c9w82GKAAAAAC/love.gif",
            "https://c.tenor.com/ZzorehuOxt8AAAAM/hug-cats.gif"

        ]

        embed.set_image(url=random.choice(gifs))
        return await ctx.send(embed=embed)

    @commands.cooldown(1, 0 if not settings.LOW_DATA_MODE else 10, commands.BucketType.user)
    @commands.command()
    async def kill(self, ctx, check: str = None):
        if check is None:
            embed = functions.error("Kill", "🚫 " + self.bot.response(2) + f" it looks like you need to specify a user.")
            return await ctx.send(embed=embed)
        try:
            member = await commands.MemberConverter().convert(ctx, check)
        except Exception as e:
            embed = functions.error("Kill", "🚫 " + self.bot.response(2) + f" I couldn't find a user named `{check}`.")
            return await ctx.send(embed=embed)
        
        embed = functions.embed("Kill", color=0xeb7d34)
        embed.description = f"{random.choice(['lmao', 'rip', 'L bozo'])} <@{member.id}> got killed by <@{ctx.author.id}>"
        return await ctx.send(embed=embed)

    @commands.cooldown(1, 0 if not settings.LOW_DATA_MODE else 10, commands.BucketType.user)
    @commands.command()
    async def ship(self, ctx, user=None, *, other=None):
        if user is None:
            embed = functions.error("Ship", "🚫 " + self.bot.response(2) + " you need to specify a user.")
            return await ctx.send(embed=embed)
        if other is None:
            embed = functions.error("Ship", "🚫 " + self.bot.response(2) + f" you need to specify something/someone to ship the user with.")
            return await ctx.send(embed=embed)
        
        try:
            member = await commands.MemberConverter().convert(ctx, user)
        except Exception as e:
            embed = functions.error("Ship", "🚫 " + self.bot.response(2) + f" I couldn't find a user named `{user}`.")
            return await ctx.send(embed=embed)

        try:
            other = await commands.MemberConverter().convert(ctx, other)
        except Exception as e:
            pass

        val = abs(hash("".join(sorted(str(member) + str(other)))))
        if random.random() < 0.1:
            val = round(val / 10, 3) # less than 10%
        if random.random() == 1.0:
            val = 100.000

        compat = round(val / (10 ** len(str(val))) * 100, 3)
        ratings = ["Never happening", "Awful", "Horrible", "Bad", "Not great", "Decent", "Fine", "Good", "Great", "Perfect"]
        embed = functions.embed("Ship", color=0xeb7d34)
        if isinstance(other, discord.Member):
            other = "<@" + str(other.id) + ">"
        embed.description = f"**<@{member.id}> + {other}**\n\nCompatibility: `{compat}%`\nRating: **{ratings[int(compat // 10)]}**"
        return await ctx.send(embed=embed)

    @commands.cooldown(1, 0 if not settings.LOW_DATA_MODE else 10, commands.BucketType.user)
    @commands.command()
    async def poke(self, ctx, check: str = None):
        if check is None:
            embed = functions.error("Poke", "🚫 " + self.bot.response(2) + f" it looks like you need to specify a user.")
            return await ctx.send(embed=embed)
        try:
            member = await commands.MemberConverter().convert(ctx, check)
        except Exception as e:
            embed = functions.error("Poke", "🚫 " + self.bot.response(2) + f" I couldn't find a user named `{check}`.")
            return await ctx.send(embed=embed)
        embed = functions.embed("Poke", color=0xeb7d34)
        embed.description = f"Ouch! <@{ctx.author.id}> poked <@{member.id}>."

        gifs = [
            "https://c.tenor.com/qkvoAoV4w3wAAAAC/poke-cute-bear.gif",
            "https://c.tenor.com/KyPxfr4AVFcAAAAC/poke.gif",
            "https://c.tenor.com/9bPsSkaKgVsAAAAC/poke-boop.gif",
            "https://c.tenor.com/my_TpYpdQX0AAAAC/yeah-im-hungry-milk-and-mocha.gif"

        ]

        embed.set_image(url=random.choice(gifs))
        return await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Social(bot))