from discord.ext import commands
import discord
import re
from .utils import context
import datetime
from datetime import datetime as dtime
import random

class DisambiguateMember(commands.IDConverter):
    async def convert(self, ctx, argument):
        # check if it's a user ID or mention
        match = self._get_id_match(argument) or re.match(r'<@!?([0-9]+)>$', argument)
 
        if match is not None:
            # exact matches, like user ID + mention should search
            # for every member we can see rather than just this guild.
            user_id = int(match.group(1))
            result = ctx.bot.get_user(user_id)
            if result is None:
                raise commands.BadArgument("Could not find this member.")
            return result

        # check if we have a discriminator:
        if len(argument) > 5 and argument[-5] == '#':
            # note: the above is true for name#discrim as well
            name, _, discriminator = argument.rpartition('#')
            pred = lambda u: u.name == name and u.discriminator == discriminator
            result = discord.utils.find(pred, ctx.bot.users)
        else:
            # disambiguate I guess
            if ctx.guild is None:
                matches = [
                    user for user in ctx.bot.users
                    if user.name == argument
                ]
                entry = str
            else:
                matches = [
                    member for member in ctx.guild.members
                    if member.name == argument
                    or (member.nick and member.nick == argument)
                ]

                def to_str(m):
                    if m.nick:
                        return f'{m} (a.k.a {m.nick})'
                    else:
                        return str(m)

                entry = to_str

            try:
                result = await ctx.disambiguate(matches, entry)
            except Exception as e:
                raise commands.BadArgument(f'Could not find this member. {e}') from None

        if result is None:
            raise commands.BadArgument("Could not find this member. Note this is case sensitive.")
        return result

ITEMS = {
	'apple':{
		'price': 5
	}
}

WEAPONS = {
	0: {
		'name': 'No weapon',
		'damage': 0,
		'description': 'No weapon',
		'price': 0,
		'emoji': None,
	},
	1: {
		'name': 'iWeeti\'s sword',
		'damage': 500,
		'description': 'Special made sword for iWeeti',
		'price': 9999999,
		'emoji': None,
	},
	2: {
		'name': 'lukee\'s sword',
		'damage': 500,
		'description': 'Special made sword for lukee',
		'price': 9999999,
		'emoji': None,
	},
	3: {
		'name': 'Excalibur',
		'damage': 50000,
		'description': 'The legendary Excalibur',
		'price': 999999999999,
		'emoji': 493479981066878987,
	},
}

class Weapon:
	def __init__(self, id):
		self.name = WEAPONS[id]['name'] or 'Not defined'
		self.damage = WEAPONS[id]['damage'] or 0
		self.description = WEAPONS[id]['description']
		self.price = WEAPONS[id]['price']
		self.emoji = WEAPONS[id]['emoji']
		self.id = id

	def __str__(self):
		return f'{self.name}: {self.damage}DMG (ID:{self.id})' if self.name else 'No weapon'
	

class Item:
	def __init__(self, name):
		self.price = ITEMS[name]['price']

class ProfileInfo:
	def __init__(self, bot, ctx, name, record):
		self.bot = bot
		self.ctx = ctx
		self.name = name
		self.record = record
		self.id = record['id']
		self.weapon = Weapon(record['weapon'])
		self.bio = record['bio']
		self.cash = record['cash'] or 0
		self.xp = record['xp'] or 0
		self.level = record['level'] or 0
		self.apples = record['apples'] or ''
		self.last_xp_time = record['last_xp_time'] or None
		self.announce_level = record['announce_level']

	def __str__(self):
		return f'Profile of {self.name}'

	@property
	def inv(self):
		inv = f'{self.apples}'
		return inv

	@property
	def is_ratelimited(self):
		if not self.last_xp_time:
			return False
		_last = eval(self.last_xp_time)
		return _last + datetime.timedelta(minutes=1) > dtime.utcnow()

	def _get_level_xp(self, n):
	    return 5*(n**2)+50*n+100

	def _get_level_from_xp(self, xp):
	    remaining_xp = int(xp)
	    level = 0
	    while remaining_xp >= self._get_level_xp(level):
	        remaining_xp -= self._get_level_xp(level)
	        level += 1
	    return level

	async def edit_field(self, **fields):
		keys = ', '.join(fields)
		values = ', '.join(f'${2 + i}' for i in range(len(fields)))

		query = f"""update profiles
		            SET {keys} = {values}
		            where id=$1;
		         """
		_values = [_ for _ in fields.values()]

		for index, key in enumerate(fields):
			self.__dict__[key] = _values[index]

		await self.bot.pool.execute(query, self.id, *fields.values())

	async def increase_xp(self, ctx):
		if self.is_ratelimited:
			return
		_now = dtime.utcnow()
		await self.edit_field(last_xp_time=repr(_now))
		new_xp = self.xp + random.randint(15, 25)
		await self.edit_field(xp=new_xp)
		lvl = self.level
		new_lvl = self._get_level_from_xp(self.xp)
		await self.edit_field(level=new_lvl)
		if new_lvl != lvl:
			if self.announce_level and not self.ctx.guild.id == 264445053596991498:
				await ctx.send(f'Good job {ctx.author.display_name} you just leveled up to level {new_lvl}!')

class Profile:
	def __init__(self, bot):
		self.bot = bot

	async def get_profile(self, ctx, member=None, auto_create=True):
		member = member or ctx.author
		id = member.id
		record = await self.bot.pool.fetchrow(f'select * from profiles where id={id}')
		if not record:
			if member is ctx.author and auto_create:
				await ctx.db.execute(f'INSERT INTO PROFILES VALUES ({member.id})')
				record = await ctx.db.fetchrow(f'SELECT * FROM PROFILES WHERE id={id}')
				return ProfileInfo(self.bot, ctx, member.name, record)
			return None
		return ProfileInfo(self.bot, ctx, member.name, record)

	@commands.group(invoke_without_command=True)
	async def profile(self, ctx, *, member: DisambiguateMember = None):
		"""Shows your or someone else's profile."""
		if not ctx.invoked_subcommand:
			member = member or ctx.author
			profile = await self.get_profile(ctx, member=member)
			if member is not ctx.author and not profile:
				return await ctx.send(f'{ctx.tick(False)} This member does not have a profile.')

			e = discord.Embed(title=str(profile), color=member.top_role.colour if member.top_role.color else ctx.me.top_role.colour)
			e.description = profile.bio
			e.set_thumbnail(url=member.avatar_url)

			e.add_field(name="Weapon", value=str(profile.weapon))
			e.add_field(name="Cash", value=f'${profile.cash}')
			e.add_field(name="XP", value=profile.xp)
			e.add_field(name="Level", value=profile.level)
			# e.add_field(name="Inventory", value=profile.inv)

			e.set_footer(text='The profiles are still in development and not fully done.\n'\
							  'Don\'t excpect them to work ideally or in anyway yet.')

			await ctx.send(embed=e)

	@profile.command(hidden=True)
	async def make(self, ctx):
		"""Makes a profile if you don't already have a one."""
		profile = await self.get_profile(ctx)
		if not profile:
			await ctx.db.execute(f'insert into profiles values({ctx.author.id})')
		await ctx.invoke(self.profile, member=ctx.author)

	@profile.command()
	async def bio(self, ctx, *, bio:str=None):
		"""Changes your profile's bio."""
		profile = await self.get_profile(ctx)

		if not bio:
			return await ctx.send(f'{ctx.tick(False)} You forgot the most important part the actual BIO.')

		await profile.edit_field(bio=bio)
		await ctx.send(f'{ctx.tick(True)} BIO edited.')

	def get_weapon(self, id):
		try:
			return Weapon(id)
		except KeyError:
			return None

	@commands.command()
	async def weaponinfo(self, ctx, id:int=0):
		"""Shows weapon's info by it's id."""
		try:
			weapon = self.get_weapon(id)
		except KeyError:
			return await ctx.send(f'{ctx.tick(False)} That weapon was not found.')

		e = discord.Embed(title=str(weapon), description=weapon.description, colour=ctx.author.top_role.colour)
		e.add_field(name="Price", value=weapon.price)
		if weapon.emoji:
			emoji = self.bot.get_emoji(weapon.emoji)
			e.set_image(url=emoji.url)

		await ctx.send(embed=e)

	async def on_message(self, message):
		if message.author.bot: return
		ctx = await self.bot.get_context(message, cls=context.Context)
		profile = await self.get_profile(ctx, auto_create=False)
		if not profile: return
		await profile.increase_xp(ctx)

	def get_item(self, name):
		try:
			return Item(name)
		except KeyError:
			return None

	@commands.group()
	async def buy(self, ctx):
		if ctx.invoked_subcommand is None:
			return ctx.show_help('buy')

	@buy.command(name='apple')
	async def buy_apple(self, ctx, amount:int=1):
		profile = await self.get_profile(ctx)

		# if profile

def setup(bot):
	bot.add_cog(Profile(bot))