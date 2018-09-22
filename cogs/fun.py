import discord
from discord.ext import commands
import requests #you only need it for a short time so its gud

class Fun():
    """Commands that will stop boredom :^)"""
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command()
    async def ascii(self, ctx, *, text):
        text = text.replace(" ", "+")
        r = requests.get(f"http://artii.herokuapp.com/make?text={text}")
        rc = str(r.content)
        rc = rc.replace("\n", "\n")
        await ctx.send(f"```{rc}```")
      
    
        

def setup(bot):
    bot.add_cog(Fun(bot))
