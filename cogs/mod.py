from discord.ext import commands
import discord
from .utils import checks
from collections import Counter


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

	async def remove_messages(self, ctx, limit, pred, before=None, after=None):
		if limit > 2000:
			return await ctx.send(f'{ctx.tick(False)} Invalid limit. {limit}/2000')

		before = discord.Object(id=before) or ctx.message

		if after is not None:
			after = discord.Object(id=after)

		try:
			deleted_messages = await ctx.channel.purge(limit=limit, before=before, after=after, check=pred)
		except discord.Forbidden:
			return await ctx.send(f'{ctx.tick(False)} I do not have delete messages permissions.')
		except discord.HTTPException as e:
			return await ctx.send(f'Oops... {e}, maybe try a smaller limit.')

		deleted_counter = Counter(m.author.display_name for m in deleted_messages)
		deleted_messages = len(deleted_messages)
		messages = [f'{deleted_messages} message{" was" if deleted_messages == 1 else "s were"} purged.']
		if deleted_messages:
		    messages.append('')
		    deleted_counter = sorted(deleted_counter.items(), key=lambda t: t[1], reverse=True)
		    messages.extend(f'**{name}**: {count}' for name, count in deleted_counter)

		to_send = '\n'.join(deleted_messages)

		if len(to_send) > 2000:
		    await ctx.send(f'{ctx.tick(True)} Successfully purged {deleted_messages} messages.', delete_after=10)
		    await asyncio.sleep(10)
		    await ctx.message.delete()
		else:
		    await ctx.send(to_send, delete_after=10)
		    await asyncio.sleep(10)
		    await ctx.message.delete()

	@commands.group()
	@checks.is_mod()
	async def purge(self, ctx):
		if not ctx.invoked_subcommand:
			return await ctx.show_help('purge')

	@purge.command(name='all')
	@checks.is_mod()
	async def purge_all(self, ctx, limit:int=100):
		await self.remove_messages(ctx, limit, lambda m: True)

	@purge.command(name='embeds', aliases=['embed'])
	@checks.is_mod()
	async def purge_embeds(self, ctx, limit:int=100):
		await self.remove_messages(ctx, limit, lambda m: len(m.embeds))

	@purge.command(name='files', aliases=['file'])
	@checks.is_mod()
	async def purge_files(self, ctx, limit:int=100):
		await self.remove_messages(ctx, limit, lambda m: len(m.attachments))

	@purge.command(name='images', aliases=['image'])
	@checks.is_mod()
	async def purge_images(self, ctx, limit:int=100):
		await self.remove_messages(ctx, limit, lambda m: len(e.embeds) or len(e.attachments))

	@purge.command(name='user', aliases=['users'])
	@checks.is_mod()
	async def purge_user(self, ctx, member:discord.Member=None, limit:int=100):
		if not member:
			return await ctx.send(f'{ctx.tick(False)} You need to specify a member to purge.')
		await self.remove_messages(ctx, limit, lambda m: m.author.id == member.id)

def setup(bot):
	bot.add_cog(Mod(bot))