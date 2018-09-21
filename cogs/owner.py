from .utils import checks
from discord.ext import commands

class Owner:
	"""Owner only commands."""
	def __init__(self, bot):
		self.bot = bot

	def __local_check(self, ctx):
        is_owner = ctx.author.id == 464910064965386283 or ctx.author.id == 396153668820402197
        if not is_owner:
        	raise commands.NotOwner
        return is_owner

	@commands.command()
	async def test(self, ctx):
		await ctx.send('test')

def setup(bot):
	bot.add_cog(Owner(bot))