import discord
from discord.ext import commands
import asyncio
import aiohttp
import requests
from colorthief import ColorThief
from io import BytesIO
import random


class NSFW():
    """These commands can only be used in NSFW-Marked Channels"""
    def __init__(self, bot):
        self.bot = bot
            
    @commands.command(aliases=["danb"])
    async def danbooru(self, ctx, *, tags=None):
        """Searches for NSFW images.
        NSFW means not safe for work.
        Basically it is just nudity and sex."""
        if not ctx.channel.is_nsfw():
            return await ctx.send(f'{ctx.tick(False)} This command can only be used at nsfw marked channels. You little pervert :smile:')
        embd = discord.Embed(description=f"**Searching** for **\"{tags}\"**..")
        embd = await ctx.send(embed=embd)
        if not tags:
            try:
                page = random.randint(1, 50)
                async with aiohttp.ClientSession() as cs:
                    async with cs.get(f"https://yande.re/post.json?limit=1&page={page}") as r:
                        r = await r.json()
                async with aiohttp.ClientSession() as cs:
                    async with cs.get(r[0]['file_url']) as response:
                        img = await response.read()
                colour_thief = ColorThief(BytesIO(img))
                colour = colour_thief.get_color(quality=15)
                link = 'https://danbooru.donmai.us/posts/' + str(r[0]['id'])
                embed = discord.Embed(colour=discord.Color.from_rgb(*colour), title=f"Random Post", url=link)
                embed.set_image(url=r[0]['file_url'])
                embed.set_footer(text=f"♥ {r[0]['score']}")
                return await embd.edit(embed=embed)
            except Exception as e:
                return await embd.edit(content=f'An error occured!\n```\n{e}```')
        try:
            tags = tags.replace(" ", "+")
            page = random.randint(1, 10)
            async with aiohttp.ClientSession() as cs:
                async with cs.get(f"https://yande.re/post.json?tags={tags}&limit=1&page={page}") as r:
                    r = await r.json()
            async with aiohttp.ClientSession() as cs:
                async with cs.get(r[0]['file_url']) as response:
                    img = await response.read()
            colour_thief = ColorThief(BytesIO(img))
            colour = colour_thief.get_color(quality=15)
            link = 'https://danbooru.donmai.us/posts/' + str(r[0]['id'])
            embed = discord.Embed(colour=discord.Color.from_rgb(*colour), title=f"\"{tags}\"", url=link)
            embed.set_image(url=r[0]['file_url'])
            embed.set_footer(text=f"♥ {r[0]['score']}")
            await embd.edit(embed=embed)
        except Exception as e:
            em = discord.Embed(title="No results found!")
            await embd.edit(embed=em)

def setup(bot):
    bot.add_cog(NSFW(bot))
