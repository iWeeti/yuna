from discord.ext import commands
import discord
import aiohttp
from cogs.utils import context
from cogs.utils.config import Config
from collections import deque
import config
from random import choice as rnd
import asyncio
import aiohttp
import requests
import datetime
import traceback
import logging
import os
from .utils.paginator import HelpPaginator, CannotPaginate

INITIAL_EXTENSIONS = [
	'owner',
	'anime',
	'config',
	'nsfw',
	'profiles',
	'music'
]

def get_prefix(bot, msg):
    """Gets the prefix for a command."""
    user_id = bot.user.id
    base = [f'<@!{user_id}> ', f'<@{user_id}> ']
    if msg.guild is None:
        base.append('.')
    else:
        base.extend(bot.prefixes.get(msg.guild.id, ['yu ', 'Yu ', 'yuna ', 'y?']))
    return base

class Yuna(commands.AutoShardedBot):
	def __init__(self):
		super().__init__(command_prefix=get_prefix)
		self.session = aiohttp.ClientSession(loop=self.loop)
		self._prev_events = deque(maxlen=10)
		self.commands_run = 0

		self.prefixes = Config('prefixes.json')
		self.remove_command('help')
		self.add_command(self.help)

		for extension in INITIAL_EXTENSIONS:
			try:
				self.load_extension(f'cogs.{extension}')
				print(f'[INFO] Loaded {extension}')
			except Exception as e:
				print(f'[FAIL] Failed to load {extension} with error: {e}')

	@commands.command(name='help', hidden=True)
	async def _help(self, ctx, *, command: str = None):
		"""Shows help about a command or the bot"""
		try:
			if command is None:
			    p = await HelpPaginator.from_bot(ctx)
			else:
			    entity = self.bot.get_cog(command) or self.bot.get_command(command)

			    if entity is None:
			        clean = command.replace('@', '@\u200b')
			        return await ctx.send(f'Command or category "{clean}" not found.')
			    elif isinstance(entity, commands.Command):
			        p = await HelpPaginator.from_command(ctx, entity)
			    else:
			        p = await HelpPaginator.from_cog(ctx, entity)

			await p.paginate()
		except Exception as e:
		    await ctx.send(e)

	@property
	def config(self):
	    """Returns the config."""
	    return __import__('config')

	async def avatar_queue(self):
		try:
			avatars = ['https://cdn.discordapp.com/attachments/488928330805018626/492776771662643200/maxresdefault.png?width=734&height=413',
				'https://media.discordapp.net/attachments/488928330805018626/492777747941163009/image0.png?width=660&height=413',
				'https://media.discordapp.net/attachments/488928330805018626/492776959588433928/878577-download-wallpaper-yuna-1961x1226-pc.png?width=660&height=413']
			while True:
				r = requests.get(rnd(avatars))
				await self.user.edit(avatar=r.content)
				await asyncio.sleep(86400)
		except Exception as e:
			print(e)
	
	async def on_ready(self):
		print(f"[INFO] I'm Alive!\n"\
			  f"[NAME] Logged in as {self.user.name}.\n"\
			  f"[ ID ] {self.user.id}")
		await self.change_presence(activity=discord.Activity(name='y?help | UwU', type=discord.ActivityType.listening))
		self.loop.create_task(self.avatar_queue())

	@property
	def error_ch(self):
		ch = self.get_channel(492797168005152778)
		return ch

	@property
	def guild_ch(self):
		ch = self.get_channel(492797204873084949)
		return ch

	async def send_guild_stats(self, e, guild):
		e.add_field(name='Name', value=guild.name)
		e.add_field(name='ID', value=guild.id)
		e.add_field(name='Owner', value=f'{guild.owner} (ID: {guild.owner.id})')

		bots = sum(m.bot for m in guild.members)
		total = guild.member_count
		online = sum(m.status is discord.Status.online for m in guild.members)
		e.add_field(name='Members', value=str(total))
		e.add_field(name='Bots', value=f'{bots} ({bots/total:.2%})')
		e.add_field(name='Online', value=f'{online} ({online/total:.2%})')

		if guild.icon:
		    e.set_thumbnail(url=guild.icon_url)

		if guild.me:
		    e.timestamp = guild.me.joined_at

		await self.guild_ch.send(embed=e)

	async def on_guild_join(self, guild):
	    e = discord.Embed(colour=0x53dda4, title='New Guild')
	    await self.send_guild_stats(e, guild)

	async def on_guild_remove(self, guild):
	    e = discord.Embed(colour=0xdd5f53, title='Left Guild')
	    await self.send_guild_stats(e, guild)

	async def on_command_error(self, ctx, error):
		try:
		    ignored = (commands.NoPrivateMessage, commands.DisabledCommand, commands.CheckFailure,
		               commands.CommandNotFound, commands.UserInputError, discord.Forbidden, commands.CommandOnCooldown)
		    error = getattr(error, 'original', error)

		    if isinstance(error, ignored):
		        return

		    e = discord.Embed(title='Command Error', colour=0xcc3366)
		    e.add_field(name='Name', value=ctx.command.qualified_name)
		    e.add_field(name='Author', value=f'{ctx.author} (ID: {ctx.author.id})')

		    fmt = f'Channel: {ctx.channel} (ID: {ctx.channel.id})'
		    if ctx.guild:
		        fmt = f'{fmt}\nGuild: {ctx.guild} (ID: {ctx.guild.id})'

		    e.add_field(name='Location', value=fmt, inline=False)

		    exc = ''.join(traceback.format_exception(type(error), error, error.__traceback__, chain=False))
		    e.description = f'```py\n{exc}\n```'
		    e.timestamp = datetime.datetime.utcnow()
		    await self.error_ch.send(embed=e)
		except Exception as e:
			print(e)

	async def on_error(self, event, *args, **kwargs):
	    e = discord.Embed(title='Event Error', colour=0xa32952)
	    e.add_field(name='Event', value=event)
	    e.description = f'```py\n{traceback.format_exc()}\n```'
	    e.timestamp = datetime.datetime.utcnow()

	    await self.error_ch.send(embed=e)

	async def on_command(self, ctx):
		"""This triggers when a command is invoked."""
		self.commands_run += 1

	def get_guild_prefixes(self, guild, *, local_inject=get_prefix):
	    """Gets the guild prefixes."""
	    proxy_msg = discord.Object(id=None)
	    proxy_msg.guild = guild
	    return local_inject(self, proxy_msg)

	def get_raw_guild_prefixes(self, guild_id):
	    """Gets the raw guild prefixes."""
	    return self.prefixes.get(guild_id, ['.'])

	async def set_guild_prefixes(self, guild, prefixes):
	    """Sets the guild prefixes."""
	    if not prefixes[0]:
	        await self.prefixes.put(guild.id, [])
	    elif len(prefixes) > 10:
	        raise RuntimeError('Cannot have more than 10 custom prefixes.')
	    else:
	        await self.prefixes.put(guild.id, sorted(set(prefixes), reverse=True))

	async def on_message(self, message):
		if message.author.bot: return

		await self.process_commands(message)

	async def on_resumed(self):
	    """This triggers when the bot resumed after an outage."""
	    print('[INFO] Resumed...')

	async def process_commands(self, message):
	    """This processes the commands."""
	    ctx = await self.get_context(message, cls=context.Context)

	    if ctx.command is None:
	        return

	    async with ctx.acquire():
	        await self.invoke(ctx)

	async def close(self):
	    await super().close()
	    await self.session.close()

	def run(self):
		try:
		    super().run(config.token, reconnect=True)
		finally:
		    with open('prev_events.log', 'w', encoding='utf-8') as _fp:
		        for data in self._prev_events:
		            try:
		                _x = json.dumps(data, ensure_ascii=True, indent=4)
		            except:
		                _fp.write(f'{data}\n')
		            else:
		                _fp.write(f'{_x}\n')
