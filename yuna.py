from discord.ext import commands
import discord
import aiohttp
from cogs.utils import context

import config

INITIAL_EXTENSIONS = [
	'',
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

		for extension in INITIAL_EXTENSIONS:
			try:
				self.load_extension(f'cogs.{extension}')
			except Exception as e:
				print(f[FAIL] Failed to load '{extension} with error: {e]')

	@property
	def config(self):
	    """Returns the config."""
	    return __import__('config')

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