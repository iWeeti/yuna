from discord.ext import commands
import discord
from .utils import checks


class Reason(commands.Converter):
	"""Converts an action reason"""
	async def convert(self, ctx, arg=None):
		if arg is None or not arg:
			return f'Action by {ctx.author} (ID:{ctx.author.id})'		
		return f'Action by {ctx.author} (ID:{ctx.author.id}): {arg}'


class Mod:
	"""Moderation related commands."""
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	@checks.is_mod()
	async def kick(self, ctx, members:commands.Greedy[discord.Member]=None, *, reason: Reason=None):
		if not members:
			return await ctx.send(f'{ctx.tick(False)} You need to specify at least one member to kick.')

		kicked = []

		for member in members:
			try:
				await member.kick(reason=reason)
				kicked.append(member.display_name)
			except discord.Forbidden:
				return await ctx.send(f'{ctx.tick(False)} Failed to kick, I need kick members permissions to do this.')

		await ctx.send(f'{ctx.tick(True)} Kicked {", ".join(kicked)}.')

	@commands.command()
	@checks.is_mod()
	async def ban(self, ctx, members:commands.Greedy[discord.Member]=None, *, reason: Reason=None):
		if not members:
			return await ctx.send(f'{ctx.tick(False)} You need to specify at least one member to ban.')

		banned = []

		for member in members:
			try:
				await ctx.guild.ban(member, reason=reason)
				banned.append(member)
			except discord.Forbidden:
				return await ctx.send(f'{ctx.tick(False)} I need ban members permissions to run this command.')

		await ctx.send(f'{ctx.tick(True)} Banned {", ".join(banned)}.')

def setup(bot):
	bot.add_cog(Mod(bot))