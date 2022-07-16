from discord.ext import commands
import functions
import random

def botembed(title):
    embed = functions.embed("Games - " + title, color=0x8f0000)
    return embed

def error(errormsg):
    embed = functions.error("Games", errormsg)
    return embed

class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def coinflip(self, ctx):
        flip = random.choice(["Heads", "Tails"])
        embed = botembed("Coin Flip")
        embed.description = f"The coin landed on **{flip.upper()}**."
        return await ctx.send(embed=embed)

    @commands.command()
    async def roll(self, ctx, sides=None, dice=None):
        if not sides:
            sides = 6
        elif sides:
            sides = sides.lower()
            if sides[0] != "d":
                embed = error("Dice Roll")
                embed.description = "🚫 " + self.bot.response(2) + " you need to enter a valid number of sides (`d[sides]`)."
                return await ctx.send(embed=embed)
            try:
                temp = int(sides[1:])
            except: 
                embed = error("Dice Roll")
                embed.description = "🚫 " + self.bot.response(2) + " you need to enter a valid number of sides (`d[sides]`)."
                return await ctx.send(embed=embed)
            if temp < 0:
                embed = error("Dice Roll")
                embed.description = "🚫 " + self.bot.response(2) + " you need to role a die with at least 1 side."
                return await ctx.send(embed=embed)
            goodsides = temp
        if dice is None:
            dice = 1
        else:
            try:
                dice = int(dice)
            except:
                embed = error("Dice Roll")
                embed.description = "🚫 " + self.bot.response(2) + " you need to enter a valid number of dice you wish to roll."
                return await ctx.send(embed=embed)  
            
        embed = botembed("Dice Roll")
        correct = "die" if dice == 1 else "dice"
        desc = f"You rolled **{dice}** {correct} with **{goodsides}** side{'s' if goodsides > 1 else ''}.\n`"
        for _ in range(dice):
            desc += str(random.randint(1, goodsides)) + ", "
        embed.description = desc[:-2] + "`"
        
        return await ctx.send(embed=embed)

    @commands.command(name="8ball")
    async def magic8ball(self, ctx, *, question=None):
        if not question:
            embed = error("8 Ball")
            embed.description = "🚫 " + self.bot.response(2) + " you need to enter a question."
            return await ctx.send(embed=embed)
        answers = ["It is certain.",
                "It is decidedly so.",
                "Without a doubt.",
                "Yes - definitely.",
                "You may rely on it.",
                "Reply hazy, try again.",
                "Ask again later.",
                "Better not tell you now.",
                "Cannot predict now.",
                "Concentrate and ask again.",
                "Don't count on it.",
                "My reply is no.",
                "My sources say no.",
                "Outlook not so good.",
                "Very doubtful."]
        reply = random.choice(answers)
        embed = botembed("8 Ball")
        embed.description = f"Question: `{question}`\nResponse: `{reply}`"
        return await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Games(bot))