from discord.ext import commands
import discord

class Profile:
	def __init__(self, bot):
		self.bot = bot



def setup(bot):
	bot.add_cog(Profile(bot))