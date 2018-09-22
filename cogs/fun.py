import discord
from discord.ext import commands


class Fun():
    """Commands that will stop boredom :^)"""
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command()
    async def ascii(self, ctx, *, text):
        text = text.replace(' ', '\n')
        
        if not text:
            await ctx.send(f"{ctx.tick(False)} You need to specify what anime you want to search for!")
            
        _fig = figlet_format(text)
        
        if len(_fig) > 1700:
            await ctx.send(f"{ctx.tick(False} The message is too long!")
        await ctx.send(f"Here you go!\n```{_fig}```")
      
    
        

def setup(bot):
    bot.add_cog(Fun(bot))
