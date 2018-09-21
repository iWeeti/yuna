import discord
from discord.ext import commands
import requests
from colorthief import ColorThief
from io import BytesIO
#^
#^
############## REQUESTTSTSTTSTSTST >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#no API's were harmed in the making of this code
class NSFW():
    """These commands can only be used in NSFW-Marked Channels"""
    def __init__(self, bot):
        self.bot = bot

    def __local_check(self, ctx):
        if not ctx.channel.is_nsfw():
            await ctx.send(f'{ctx.tick(False)} This command can only be used at nsfw marked channels. You little pervert :smile:')
            return

    @commands.command(aliases=["danb"])
    @commands.is_nsfw()
    async def danbooru(self, ctx, *, tags=None):
        embd = discord.Embed(description=f"**Searching** for **\"{tags}\"**..")
        embd = await ctx.send(embed=embd)
        if tags is not None:
            try:
                tags = tags.replace(" ", "+")
                page = random.randint(1, 10)
                r = requests.get(f"https://yande.re/post.json?tags={tags}&limit=1&page={page}").json()
                f = r[0]['file_url']
                img = requests.get(f)
                colour_thief = ColorThief(BytesIO(img.content))
                colour = colour_thief.get_color(quality=15)
                link = 'https://danbooru.donmai.us/posts/' + str(r[0]['id'])
                embed = discord.Embed(colour=discord.Color.from_rgb(*colour), title=f"\"{tags}\"", url=link)
                embed.set_image(url=f)
                embed.set_footer(text=f"♥ {r[0]['score']}")
                await embd.edit(embed=embed)
            except Exception as e:
                em = discord.Embed(title="No results found!")
                await embd.edit(embed=em)
        else:
            try:
                page = random.randint(1, 50)
                r = requests.get(f"https://yande.re/post.json?limit=1&page={page}").json()
                f = r[0]['file_url']
                img = requests.get(f)
                colour_thief = ColorThief(BytesIO(img.content))
                colour = colour_thief.get_color(quality=13)
                link = 'https://danbooru.donmai.us/posts/' + str(r[0]['id'])
                embed = discord.Embed(colour=discord.Color.from_rgb(*colour), title=f"Random Post", url=link)
                embed.set_image(url=f)
                embed.set_footer(text=f"♥ {r[0]['score']}")
                await embd.edit(embed=embed)
            except Exception as e:
                await embd.edit(content=f'An error occured!\n```\n{e}```')


def setup(bot):
    bot.add_cog(NSFW(bot))
