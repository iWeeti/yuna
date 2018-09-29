import discord
from discord.ext import commands
from pyfiglet import *
from chewey import chewey


class Fun():
    """Commands that will stop boredom :^)"""
    def __init__(self, bot):
        self.bot = bot
        self.chewey = chewey.Client(bot.config.chewey_token)
        
    @commands.command()
    async def ascii(self, ctx, *, text):
        """Convert your text to ASCII"""
        text = text.replace(' ', '\n')
        
        if not text:
            await ctx.send(f"{ctx.tick(False)} You need to specify the text you want to convert!")
            
        _fig = figlet_format(text.replace(' ', '\n'))
        
        if len(_fig) > 1300:
            await ctx.send(f"{ctx.tick(False)} That message is too long!")
        await ctx.send(f"{ctx.tick(True)} Done!")
        await ctx.send(f"```{_fig}```")

    @commands.command()
    async def gay(self, ctx, member:discord.Member=None, member2:discord.Member=None):
        if not member:
            return await ctx.send(f'{ctx.tick(False)} You need to specify at least one member to gay.')

        if not member2:
            member2 = ctx.author

        e = discord.Embed()
        e.set_image(url=f'https://kaan.ga/iWeeti/gayify/{member.id}/{member.avatar}/{member2.id}/{member2.avatar}/')

        await ctx.send(embed=e)

    @commands.command()
    async def dog(self, ctx):


def setup(bot):
    bot.add_cog(Fun(bot))
