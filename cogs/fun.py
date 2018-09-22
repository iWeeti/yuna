import discord
from discord.ext import commands
from pyfiglet import *


class Fun():
    """Commands that will stop boredom :^)"""
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command()
    async def ascii(self, ctx, *, text):
        """Convert your text to ASCII"""
        text = text.replace(' ', '\n')
        
        if not text:
            await ctx.send(f"{ctx.tick(False)} You need to specify the text you want to convert!")
            
        _fig = figlet_format(text)
        
        if len(_fig) > 1300:
            await ctx.send(f"{ctx.tick(False)} That message is too long!")
        await ctx.send(f"Here you go!\n```{_fig}```")
      
    
        

def setup(bot):
    bot.add_cog(Fun(bot))
