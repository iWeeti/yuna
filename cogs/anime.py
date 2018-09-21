import discord
from discord.ext import commands
import nekos

class Anime():
    """These commands work with nekos.life api."""
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def tickle(self, ctx, *, member: discord.Member=None):
        """Ticles a member you specify."""
        if member is None:
            await ctx.send('You need to specify a user you want to tickle.')
            return
        e = discord.Embed(title="{} has been tickled by {}.".format(member.name, ctx.author.name), color=ctx.author.top_role.color)
        e.set_image(url=nekos.img('tickle'))
        await ctx.send(embed=e)

    @commands.command()
    async def feed(self, ctx, *, member: discord.Member=None):
        """Feeds a member you specify."""
        if member is None:
            await ctx.send('You need to specify a user you want to feed.')
            return
        if member.id == ctx.author.id:
            await ctx.send('Go eat on your own you don\'t need help with that.')
            return
        e = discord.Embed(title="{} has been fed by {}.".format(member.name, ctx.author.name), color=ctx.author.top_role.color)
        e.set_image(url=nekos.img('feed'))
        await ctx.send(embed=e)

    @commands.command()
    async def gecg(self, ctx):
        """Gives you a gecg image."""
        e = discord.Embed(title="Here is a feet gecg for you {}.".format(ctx.author.name), color=ctx.author.top_role.color)
        e.set_image(url=nekos.img('gecg'))
        await ctx.send(embed=e)

    @commands.command()
    async def kemonomimi(self, ctx):
        """Gives you a kemonomimi image."""
        e = discord.Embed(title="Here is a kemonomimi image for you {}.".format(ctx.author.name), color=ctx.author.top_role.color)
        e.set_image(url=nekos.img('kemonomimi'))
        await ctx.send(embed=e)

    @commands.command()
    async def gasm(self, ctx):
        """Gives you a gasm image."""
        e = discord.Embed(title="Here is a gasm image for you {}.".format(ctx.author.name), color=ctx.author.top_role.color)
        e.set_image(url=nekos.img('gasm'))
        await ctx.send(embed=e)

    @commands.command()
    async def avatar(self, ctx):
        """Gives you a avatar image."""
        e = discord.Embed(title="Here is a avatar image for you {}.".format(ctx.author.name), color=ctx.author.top_role.color)
        e.set_image(url=nekos.img('avatar'))
        await ctx.send(embed=e)

    @commands.command()
    async def wallpaper(self, ctx):
        """Gives you a wallpaper image."""
        e = discord.Embed(title="Here is a wallpaper image for you {}.".format(ctx.author.name), color=ctx.author.top_role.color)
        e.set_image(url=nekos.img('wallpaper'))
        await ctx.send(embed=e)

    @commands.command()
    async def poke(self, ctx, member: discord.Member=None):
        """Pokes someone you mention."""
        if member is None:
            await ctx.send('You need to tell who to poke.')
            return
        if member.id == ctx.author.id:
            await ctx.send('I find this very weird. I mean like even weirder than me...')
            return
        e = discord.Embed(title="{} has been poked by {}.".format(member.name, ctx.author.name), color=ctx.author.top_role.color)
        e.set_image(url=nekos.img('poke'))
        await ctx.send(embed=e)

    @commands.command()
    async def slap(self, ctx, member: discord.Member=None):
        """Slaps someone you mention."""
        if member is None:
            await ctx.send('You need to tell who to slap.')
            return
        if member.id == ctx.author.id:
            await ctx.send('I find this very weird. Why would you slap yourself?\nDid you do something stupid?')
            return
        e = discord.Embed(title="{} has been slapped by {}.".format(member.name, ctx.author.name), color=ctx.author.top_role.color)
        e.set_image(url=nekos.img('slap'))
        await ctx.send(embed=e)

    @commands.command()
    async def pat(self, ctx, member: discord.Member=None):
        """Pats someone you mention."""
        if member is None:
            await ctx.send('You need to tell who to pat.')
            return
        if member.id == ctx.author.id:
            await ctx.send('Why would you pat yourself? Are you lonely and got nobody to pat you?')
            return
        e = discord.Embed(title="{} has been patted by {}.".format(member.name, ctx.author.name), color=ctx.author.top_role.color)
        e.set_image(url=nekos.img('pat'))
        await ctx.send(embed=e)

    @commands.command()
    async def kiss(self, ctx, member: discord.Member=None):
        """Kisses someone you mention."""
        if member is None:
            await ctx.send('You need to tell who to kiss.')
            return
        if member.id == ctx.author.id:
            await ctx.send('How is that even possible?')
            return
        e = discord.Embed(title="{} has been kissed by {}.".format(member.name, ctx.author.name), color=ctx.author.top_role.color)
        e.set_image(url=nekos.img('kiss'))
        await ctx.send(embed=e)

    @commands.command()
    async def hug(self, ctx, member: discord.Member=None):
        """Hugs someone you mention."""
        if member is None:
            await ctx.send('You need to tell who to hug.')
            return
        if member.id == ctx.author.id:
            await ctx.send('You can try to put your arms around you if you think it is enough to hug yourself?')
            return
        e = discord.Embed(title="{} has been hugged by {}.".format(member.name, ctx.author.name), color=ctx.author.top_role.color)
        e.set_image(url=nekos.img('hug'))
        await ctx.send(embed=e)

    @commands.command()
    async def cuddle(self, ctx, member: discord.Member=None):
        """Cuddles someone you mention."""
        if member is None:
            await ctx.send('You need to tell who to cuddle with.')
            return
        if member.id == ctx.author.id:
            await ctx.send('How is that even possible?')
            return
        e = discord.Embed(title="{} has cuddled with {}.".format(member.name, ctx.author.name), color=ctx.author.top_role.color)
        e.set_image(url=nekos.img('cuddle'))
        await ctx.send(embed=e)

    @commands.command()
    async def neko(self, ctx):
        """Gives you a neko image."""
        if not ctx.channel.is_nsfw():
            await ctx.send(':warning: These commands can only be used at nsfw marked channels. Silly :smile:')
            return
        e = discord.Embed(title="Here is a neko image for you {}.".format(ctx.author.name), color=ctx.author.top_role.color)
        e.set_image(url=nekos.img('neko'))
        await ctx.send(embed=e)

    @commands.command()
    async def holo(self, ctx):
        """Gives you a holo image."""
        e = discord.Embed(title="Here is a holo image for you {}.".format(ctx.author.name), color=ctx.author.top_role.color)
        e.set_image(url=nekos.img('holo'))
        await ctx.send(embed=e)

    @commands.command()
    async def waifu(self, ctx):
        """Gives you a waifu image."""
        e = discord.Embed(title="Here is a waifu image for you {}.".format(ctx.author.name), color=ctx.author.top_role.color)
        e.set_image(url=nekos.img('waifu'))
        await ctx.send(embed=e)

def setup(bot):
    bot.add_cog(Anime(bot))
