from discord.ext import commands
import discord

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

WEAPON_NAMES = {
		0: 'No weapon'
	}
WEAPON_DAMAGES = {
	0: 0
}

class Weapon:
	def __init__(self, weapon_id):
		self.name = WEAPON_NAMES[weapon_id] or 'Not defined'
		self.damage = WEAPON_DAMAGES[weapon_id] or 0

	def __str__(self):
		return f'{self.name}: {self.damage}DMG' if self.name else 'No weapon'

class ProfileInfo:
	def __init__(self, bot, ctx, name, record):
		self.bot = bot
		self.ctx = ctx
		self.name = name
		self.record = record
		self.id = record['id']
		self.weapon = Weapon(record['weapon'])
		self.bio = record['bio']

	def __str__(self):
		return f'Profile of {self.name}'

	async def edit_field(self, **fields):
		keys = ', '.join(fields)
		values = ', '.join(f'${2 + i}' for i in range(len(fields)))

		query = f"""update profiles
		            SET {keys} = {values}
		            where id=$1;
		         """

		await self.ctx.db.execute(query, self.id, *fields.values())

class Profile:
	def __init__(self, bot):
		self.bot = bot

	async def get_profile(self, ctx, *, member):
		id = member.id or ctx.author.id
		record = await self.bot.pool.fetchrow(f'select * from profiles where id={id}')
		return ProfileInfo(self.bot, ctx, member.name, record)

	@commands.group(invoke_without_command=True)
	async def profile(self, ctx, *, member: DisambiguateMember = None):
		member = member or ctx.author
		profile = await self.get_profile(ctx, member=member)

		e = discord.Embed(title=str(profile), color=member.top_role.colour or ctx.me.top_role.colour)
		e.description = profile.bio
		e.set_thumbnail(url=member.avatar_url)

		e.add_field(name="Weapon", value=str(profile.weapon))

		await ctx.send(embed=e)

def setup(bot):
	bot.add_cog(Profile(bot))