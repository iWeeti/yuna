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

INITIAL_EXTENSIONS = [
	'owner'
]

def get_prefix(bot, msg):
    """Gets the prefix for a command."""
    user_id = bot.user.id
    base = [f'<@!{user_id}> ', f'<@{user_id}> ']
    if msg.guild is None:
        base.append('.')
    else:
        base.extend(bot.prefixes.get(msg.guild.id, ['yu ', 'yuna ', 'y?']))
    return base

class Yuna(commands.AutoShardedBot):
	def __init__(self):
		super().__init__(command_prefix=get_prefix)
		self.session = aiohttp.ClientSession(loop=self.loop)
		self._prev_events = deque(maxlen=10)

		self.prefixes = Config('prefixes.json')

		for extension in INITIAL_EXTENSIONS:
			try:
				self.load_extension(f'cogs.{extension}')
			except Exception as e:
				print(f'[FAIL] Failed to load {extension} with error: {e}')

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
				async with aiohttp.ClientSession() as cs:
					async with cs.get(rnd(avatars)) as r:
						await self.user.edit(avatar=r)
				await asyncio.sleep(86400)
		except Exception as e:
			print(e)
	
	async def on_ready(self):
		print(f"\nI'm Alive!\nLogged in as {self.user.name}.")
		self.loop.create_task(self.avatar_queue())

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
