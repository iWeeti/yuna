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

class ProfileInfo:
	def __init__(self, bot, record):
		self.bot = bot
		self.record = record
		self.id = record['id']
		self.weapon = record['weapon']

	def __str__(self):
		user = ctx.guild.get_member(self.id) or await self.bot.get_user_info(self.id)
		return f'Profile of {user.display_name}'

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

	async def get_profile(self, ctx, *, id):
		if not id:
			id = ctx.author.id
		record = self.bot.pool.fetchrow(f'select * from profiles where id={id}')
		return ProfileInfo(ctx, record)

	@commands.group(invoke_without_command=True)
	async def profile(self, ctx, *, member: DisambiguateMember = None):
		member = member or ctx.author
		profile = await self.get_profile(ctx, id=member.id)
		await ctx.send(profile.weapon or 'No weapon' + str(profile))

def setup(bot):
	bot.add_cog(Profile(bot))