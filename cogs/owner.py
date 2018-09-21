from .utils import checks
from discord.ext import commands

class Owner:
	"""Owner only commands."""
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	@checks.is_owner()
	async def test(self, ctx):
		await ctx.send('test')

def setup(bot):
	bot.add_cog(Owner(bot))