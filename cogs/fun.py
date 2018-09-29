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
        e = discord.Embed(title="Dog", color=ctx.author.top_role.color)
        e.set_image(url=await self.chewey.dog())
        await ctx.send(embed=e)

    @commands.command()
    async def cat(self, ctx):
        e = discord.Embed(title="Cat", color=ctx.author.top_role.color)
        e.set_image(url=await self.chewey.cat())
        await ctx.send(embed=e)

    @commands.command()
    async def birb(self, ctx):
        e = discord.Embed(title="Birb", color=ctx.author.top_role.color)
        e.set_image(url=await self.chewey.birb())
        await ctx.send(embed=e)

    @commands.command()
    async def space(self, ctx):
        e = discord.Embed(title="Space", color=ctx.author.top_role.color)
        e.set_image(url=await self.chewey.space())
        await ctx.send(embed=e)

    @commands.command()
    async def nature(self, ctx):
        e = discord.Embed(title="Nature", color=ctx.author.top_role.color)
        e.set_image(url=await self.chewey.nature())
        await ctx.send(embed=e)

    @commands.command()
    async def otter(self, ctx):
        e = discord.Embed(title="Otter", color=ctx.author.top_role.color)
        e.set_image(url=await self.chewey.otter())
        await ctx.send(embed=e)

    @commands.command()
    async def plane(self, ctx):
        e = discord.Embed(title="Otter", color=ctx.author.top_role.color)
        e.set_image(url=await self.chewey.otter())
        await ctx.send(embed=e)

def setup(bot):
    bot.add_cog(Fun(bot))
