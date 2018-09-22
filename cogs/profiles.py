from discord.ext import commands
import discord
import re

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

class Item:
	def __init__(self, item_id):
		self.item_id

WEAPONS = {
	0: {
		'name': 'No weapon',
		'damage': 0,
		'description': 'No weapon',
		'price': 0
	},
	1: {
		'name': 'iWeeti\'s sword',
		'damage': 500,
		'description': 'Special made sword for iWeeti',
		'price': 9999999
	},
	2: {
		'name': 'lukee\'s sword',
		'damage': 500,
		'description': 'Special made sword for lukee',
		'price': 9999999
	},
}
class Weapon:
	def __init__(self, weapon_id):
		self.name = WEAPONS[weapon_id]['name'] or 'Not defined'
		self.damage = WEAPONS[weapon_id]['damage'] or 0
		self.description = WEAPONS[weapon_id]['description']
		self.price = WEAPONS[weapon_id]['price']
		self.id = weapon_id

	def __str__(self):
		return f'{self.name}: {self.damage}DMG (ID:{self.id})' if self.name else 'No weapon'

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

	def __str__(self):
		return f'Profile of {self.name}'

	@staticmethod
	def _get_level_xp(n):
	    return 5*(n**2)+50*n+100

	@staticmethod
	def _get_level_from_xp(xp):
	    remaining_xp = int(xp)
	    level = 0
	    while remaining_xp >= Profile._get_level_xp(level):
	        remaining_xp -= Profile._get_level_xp(level)
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

		for key, value in fields:
			self.__dict__[key] = _values[value]
		await self.ctx.db.execute(query, self.id, *fields.values())

	async def increase_xp(self, ctx):
	    if self.is_ratelimited:
	        return
	    if not self.last_xp_time:
	        _now = dtime.utcnow()
	        await self.edit_field(ctx, last_xp_time=repr(_now))
	    else:
	        last_xp_time = dtime.utcnow()
	        await self.edit_field(ctx, last_xp_time=repr(last_xp_time))
	    new_xp = self.xp + random.randint(15, 25)
	    await self.edit_field(self.ctx, experience=new_xp)
	    lvl = self.level
	    new_lvl = Profile._get_level_from_xp(self.xp)
	    await self.edit_field(ctx, level=new_lvl)
	    if new_lvl != lvl:
	        if self.announce_level and not ctx.guild.id == 264445053596991498:
	            await ctx.send(f'Good job {ctx.author.display_name} you just leveled up to level {new_lvl}!')

class Profile:
	def __init__(self, bot):
		self.bot = bot

	async def get_profile(self, ctx, member=None):
		member = member or ctx.author
		id = member.id
		record = await self.bot.pool.fetchrow(f'select * from profiles where id={id}')
		if not record:
			if member is ctx.author:
				await ctx.db.execute(f'INSERT INTO PROFILES VALUES ({member.id})')
				record = await ctx.db.fetchrow(f'SELECT * FROM PROFILES WHERE id={id}')
				return ProfileInfo(self.bot, ctx, member.name, record)
			return None
		return ProfileInfo(self.bot, ctx, member.name, record)

	@commands.group(invoke_without_command=True)
	async def profile(self, ctx, *, member: DisambiguateMember = None):
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

			await ctx.send(embed=e)

	@profile.command(hidden=True)
	async def make(self, ctx):
		profile = await self.get_profile(ctx)
		if not profile:
			await ctx.db.execute(f'insert into profiles values({ctx.author.id})')
		await ctx.invoke(self.profile, member=ctx.author)

	@profile.command()
	async def bio(self, ctx, bio:str=None):
		profile = await self.get_profile(ctx)

		if not bio:
			return await ctx.send(f'{ctx.tick(False)} You forgot the most important part the actual BIO.')

		await profile.edit_field(bio=bio)
		await ctx.send(f'{ctx.tick(True)} BIO edited.')
		await ctx.send(profile.__dict__)

	def get_weapon(self, id):
		return Weapon(id)

	@commands.command()
	async def weaponinfo(self, ctx, id:int=0):
		try:
			weapon = self.get_weapon(id)
		except KeyError:
			return await ctx.send(f'{ctx.tick(False)} That weapon was not found.')

		e = discord.Embed(title=str(weapon), description=weapon.description, colour=ctx.author.top_role.colour)
		e.add_field(name="Price", value=weapon.price)

		await ctx.send(embed=e)

def setup(bot):
	bot.add_cog(Profile(bot))