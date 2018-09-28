from discord.ext import commands
from .utils import checks


class Reason(commands.Converter):
	"""Converts an action reason"""
	async def convert(self, ctx, arg):
		if not arg:
			return f'Action by {ctx.author} (ID:{ctx.author.id})'		
		return f'Action by {ctx.author} (ID:{ctx.author.id}): {arg}'


class Mod:
	"""Moderation related commands."""
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	@checks.is_mod()
	async def test(self, ctx, *, test: Reason):
		await ctx.send(test)

def setup(bot):
	bot.add_cog(Mod(bot))