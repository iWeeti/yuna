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

	async def run_cmd(self, cmd: str) -> str:
	        process =\
	            await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
	        results = await process.communicate()
	        return "".join(x.decode("utf-8") for x in results)
	    
	@commands.command(hidden=True)
	async def shell(self, ctx, *, code:str):
	    x = await self.run_cmd(code)
	    await ctx.send(f'```bash\n{x}\n```')

	@commands.command(hidden=True)
	async def update(self, ctx):
	    msg = await ctx.send('Updating...')
	    x = await self.run_cmd('git pull')
	    x = x.replace('Merge made by the \'recursive\' strategy.', '')
	    x = x.replace('From https://github.com/iWeeti/yuna', '')
	    await msg.edit(content=f'```bash\n{x}\n```')

def setup(bot):
	bot.add_cog(Owner(bot))