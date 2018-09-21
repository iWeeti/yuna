import logging
import math
import re
import datetime

import random
import config
from .utils.paginator import Pages
from .utils import db

import discord
import lavalink
from discord.ext import commands

time_rx = re.compile('[0-9]+')
url_rx = re.compile('https?:\/\/(?:www\.)?.+')

class Playlists(db.Table):
    id = author_id = db.Column(db.Integer(big=True))

class Music:
    def __init__(self, bot):
        self.bot = bot

        if not hasattr(bot, 'lavalink'):
            lavalink.Client(bot=bot, password=config.lava_pass, ws_port=5000, loop=self.bot.loop, log_level=logging.WARNING)
            self.bot.lavalink.register_hook(self.track_hook)

    async def track_hook(self, event):
        if isinstance(event, lavalink.Events.TrackStartEvent):
            c = event.player.fetch('channel')
            if c:
                c = self.bot.get_channel(c)
                if c:
                    if c.members == 1:
                        event.player.queue.clear()
                        await event.player.disconnect()
                        return
                    embed = discord.Embed(colour=c.guild.me.top_role.colour, title='Now Playing', description=event.track.title)
                    embed.timestamp = datetime.datetime.utcnow()
                    requester = await self.bot.get_user_info(event.track.requester)
                    embed.set_footer(text='Requested by ' + requester.name)
                    embed.set_thumbnail(url=event.track.thumbnail)
                    await c.send(embed=embed)
        elif isinstance(event, lavalink.Events.QueueEndEvent):
            c = event.player.fetch('channel')
            if c:
                c = self.bot.get_channel(c)
                if c:
                    if c.members == 1:
                        event.player.queue.clear()
                        await event.player.disconnect()
                        return
                    await c.send('There is no more songs in the queue. Why not add some more?')

    @commands.command(aliases=['p', 'sing'])
    async def play(self, ctx, *, query):
        """Plays a song.
        You can search from:
          -youtube
          -bandcamp
          -soundcloud
          -twitch
          -vimeo
          -mixer"""
        player = self.bot.lavalink.players.get(ctx.guild.id)

        if not player.is_connected:
            if not ctx.author.voice or not ctx.author.voice.channel:
                return await ctx.send('Join a voice channel first!')

            permissions = ctx.author.voice.channel.permissions_for(ctx.me)

            if not permissions.connect or not permissions.speak:
                return await ctx.send('Missing permissions `CONNECT` and/or `SPEAK`.')

            player.store('channel', ctx.channel.id)
            await player.connect(ctx.author.voice.channel.id)
        else:
            if not ctx.author.voice or not ctx.author.voice.channel or player.connected_channel.id != ctx.author.voice.channel.id:
                return await ctx.send('Join my voice channel!')

        query = query.strip('<>')

        if not url_rx.match(query):
            query = f'ytsearch:{query}'

        results = await self.bot.lavalink.get_tracks(query)

        if not results or not results['tracks']:
            return await ctx.send('Nothing found!')

        embed = discord.Embed(colour=ctx.guild.me.top_role.colour)

        if results['loadType'] == "PLAYLIST_LOADED":
            tracks = results['tracks']

            for track in tracks:
                player.add(requester=ctx.author.id, track=track)

            embed.title = "Playlist Enqueued!"
            embed.description = f"{results['playlistInfo']['name']} - {len(tracks)} tracks"
            await ctx.send(embed=embed)
        else:
            if player.is_playing:
                track = results['tracks'][0]
                embed.title = "Song Enqueued"
                embed.description = f'[{track["info"]["title"]}]({track["info"]["uri"]})'
                await ctx.send(embed=embed)
                player.add(requester=ctx.author.id, track=track)
            else:
                track = results['tracks'][0]
                player.add(requester=ctx.author.id, track=track)

        if not player.is_playing:
            await player.play()

    @commands.command(aliases=['r', 'random'])
    async def radio(self, ctx):
        """Plays music from random radio playlist."""
        player = self.bot.lavalink.players.get(ctx.guild.id)

        if not player.is_connected:
            if not ctx.author.voice or not ctx.author.voice.channel:
                return await ctx.send('Join a voice channel first!')

            permissions = ctx.author.voice.channel.permissions_for(ctx.me)

            if not permissions.connect or not permissions.speak:
                return await ctx.send('Missing permissions `CONNECT` and/or `SPEAK`.')

            player.store('channel', ctx.channel.id)
            await player.connect(ctx.author.voice.channel.id)
        else:
            if not ctx.author.voice or not ctx.author.voice.channel or player.connected_channel.id != ctx.author.voice.channel.id:
                return await ctx.send('Join my voice channel!')

        list = 'https://www.youtube.com/watch?v=aJOTlE1K90k&list=PLw-VjHDlEOgvtnnnqWlTqByAtC7tXBg6D'

        query = list

        results = await self.bot.lavalink.get_tracks(query)

        embed = discord.Embed(colour=ctx.guild.me.top_role.colour)

        if results['loadType'] == "PLAYLIST_LOADED":
            tracks = results['tracks']

            for track in tracks:
                player.add(requester=ctx.author.id, track=track)

            embed.title = "Radio Playlist Enqueued!"
            embed.description = f"{results['playlistInfo']['name']} - {len(tracks)} tracks"
            embed.set_footer(text='I also enabled shuffle so that the music will get randomised.')
        else:
            if player.is_playing:
                track = results['tracks'][0]
                embed.title = "Radio stream enqueued"
                embed.description = '[Pop Songs World 2018 - The Best Songs Of Spotify 2018 || Live Stream 24/7](https://www.youtube.com/watch?v=QMrJ-L-FfM0)'
                await ctx.send(embed=embed)
                player.add(requester=ctx.author.id, track=track)
            else:
                track = results['tracks'][0]
                embed.title = "Radio stream enqueued"
                embed.description = '[Pop Songs World 2018 - The Best Songs Of Spotify 2018 || Live Stream 24/7](https://www.youtube.com/watch?v=QMrJ-L-FfM0)'
                player.add(requester=ctx.author.id, track=track)

        await ctx.send(embed=embed)

        if not player.shuffle:
            player.shuffle=True

        if not player.is_playing:
            await player.play()

    @commands.command()
    async def seek(self, ctx, time):
        """Seeks the track."""
        player = self.bot.lavalink.players.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send('Not playing.')

        if not ctx.author.voice or not ctx.author.voice.channel or player.connected_channel.id != ctx.author.voice.channel.id:
                return await ctx.send('Join my voice channel!')

        seconds = time_rx.search(time)

        if not seconds:
            return await ctx.send('You need to specify the amount of seconds to skip!')

        seconds = int(seconds.group()) * 1000

        if time.startswith('-'):
            seconds *= -1

        track_time = player.position + seconds

        await player.seek(track_time)

        await ctx.send(f'Moved track to **{lavalink.Utils.format_time(track_time)}**')

    @commands.command(aliases=['forceskip', 'fs'])
    async def skip(self, ctx):
        """Skips the song."""
        player = self.bot.lavalink.players.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send('Not playing.')

        if not ctx.author.voice or not ctx.author.voice.channel or player.connected_channel.id != ctx.author.voice.channel.id:
                return await ctx.send('Join my voice channel!')

        await ctx.send('⏭ | Skipped.')
        await player.skip()

    @commands.command()
    async def stop(self, ctx):
        """Stops the player and clears the queue."""
        player = self.bot.lavalink.players.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send('Not playing.')

        if not ctx.author.voice or not ctx.author.voice.channel or player.connected_channel.id != ctx.author.voice.channel.id:
                return await ctx.send('Join my voice channel!')

        player.queue.clear()
        await player.stop()
        await ctx.send('⏹ | Stopped.')

    @commands.command(aliases=['np', 'n'])
    async def now(self, ctx):
        """Shows what's playing right now."""
        player = self.bot.lavalink.players.get(ctx.guild.id)
        song = 'Nothing'

        if player.current:
            pos = lavalink.Utils.format_time(player.position)
            if player.current.stream:
                dur = 'LIVE'
            else:
                dur = lavalink.Utils.format_time(player.current.duration)
            song = f'**[{player.current.title}]({player.current.uri})**\n({pos}/{dur})'

        embed = discord.Embed(colour=ctx.guild.me.top_role.colour, title='Now Playing', description=song)
        requester = await self.bot.get_user_info(player.current.requester)
        embed.set_thumbnail(url=player.current.thumbnail)
        embed.timestamp = datetime.datetime.utcnow()
        embed.set_footer(text='Requested by ' + requester.name)
        await ctx.send(embed=embed)

    @commands.command(aliases=['q'])
    async def queue(self, ctx):
        """Shows the queue."""
        player = self.bot.lavalink.players.get(ctx.guild.id)

        if not player.queue:
            return await ctx.send('There\'s nothing in the queue! Why not queue something?')

        queue_list = []

        for track in player.queue:
            queue_list.append(f'[**{track.title}**]({track.uri})')

        # embed = discord.Embed(colour=ctx.guild.me.top_role.colour,
        #                       description=f'**{len(player.queue)} tracks**\n\n{queue_list}')
        total_length = 0
        for song in player.queue:
            total_length += song.duration
        m, s = divmod(round(total_length/1000), 60)
        h = None
        if m >= 60:
            h, m = divmod(m, 60)
        if h:
            if h >= 2:
                hours = f'{h}hours '
            elif h == 0:
                hours = ''
            else:
                hours = f'{h}hour '
            ##########################
            if m >= 2:
                minutes = f'{m}minutes '
            elif m == 0:
                minutes = ''
            else:
                minutes = f'{m}minute '
            ##########################
            if s >= 2:
                seconds = f'{s}seconds'
            elif s == 0:
                seconds = ''
            else:
                seconds = f'{s}second'
            total_length = hours + minutes + seconds
        else:
            if m >= 2:
                minutes = f'{m}minutes '
            elif m == 0:
                minutes = ''
            else:
                minutes = f'{m}minute '
            ##########################
            if s >= 2:
                seconds = f'{s}seconds'
            elif s == 0:
                seconds = ''
            else:
                seconds = f'{s}second'
            total_length = minutes + seconds
        # embed.set_footer(text=f'Viewing page {page}/{pages} | Total length {total_length}')
        # embed.timestamp = datetime.datetime.utcnow()
        # await ctx.send(embed=embed)
        try:
            p = Pages(ctx, entries=queue_list, per_page=10, show_entry_count=True)
            # p.embed.title = str(base)
            p.embed.timestamp = datetime.datetime.utcnow()
            p.embed.title=f'{len(player.queue)} tracks | Total length {total_length}'
            await p.paginate()
        except Exception as e:
            await ctx.send(e)

    @commands.command(aliases=['resume'])
    async def pause(self, ctx):
        """Pauses or resumes the track."""
        player = self.bot.lavalink.players.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send('Not playing.')

        if not ctx.author.voice or not ctx.author.voice.channel or player.connected_channel.id != ctx.author.voice.channel.id:
                return await ctx.send('Join my voice channel!')

        if player.paused:
            await player.set_pause(False)
            await ctx.send('⏯ | Resumed')
        else:
            await player.set_pause(True)
            await ctx.send('⏯ | Paused')

    @commands.command(aliases=['vol'])
    async def volume(self, ctx, volume: int=None):
        """Sets the volume."""
        player = self.bot.lavalink.players.get(ctx.guild.id)

        if not volume:
            return await ctx.send(f'🔈 | {player.volume}%')

        if not ctx.author.voice or not ctx.author.voice.channel or player.connected_channel.id != ctx.author.voice.channel.id:
                return await ctx.send('Join my voice channel!')

        await player.set_volume(volume)
        await ctx.send(f'🔈 | Set to {player.volume}%')

    @commands.command()
    async def shuffle(self, ctx):
        """Shuffles the queue."""
        player = self.bot.lavalink.players.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send('Nothing playing.')

        if not ctx.author.voice or not ctx.author.voice.channel or player.connected_channel.id != ctx.author.voice.channel.id:
                return await ctx.send('Join my voice channel!')

        player.shuffle = not player.shuffle

        await ctx.send('🔀 | Shuffle ' + ('enabled' if player.shuffle else 'disabled'))

    @commands.command()
    async def repeat(self, ctx):
        """Repeats the current queue."""
        player = self.bot.lavalink.players.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send('Nothing playing.')

        if not ctx.author.voice or not ctx.author.voice.channel or player.connected_channel.id != ctx.author.voice.channel.id:
                return await ctx.send('Join my voice channel!')

        player.repeat = not player.repeat

        await ctx.send('🔁 | Repeat ' + ('enabled' if player.repeat else 'disabled'))

    @commands.command()
    async def remove(self, ctx, index: int):
        """Removes a song from the queue."""
        player = self.bot.lavalink.players.get(ctx.guild.id)

        if not player.queue:
            return await ctx.send('Nothing queued.')

        if not index:
            index = len(player.queue)

        if not ctx.author.voice or not ctx.author.voice.channel or player.connected_channel.id != ctx.author.voice.channel.id:
                return await ctx.send('Join my voice channel!')

        if index > len(player.queue) or index < 1:
            return await ctx.send('Index has to be >=1 and <=queue size')

        index -= 1
        removed = player.queue.pop(index)

        await ctx.send('Removed **' + removed.title + '** from the queue.')

    @commands.command()
    async def find(self, ctx, *, query):
        """Searches a song from youtube."""
        if not query.startswith('ytsearch:') and not query.startswith('scsearch:'):
            query = 'ytsearch:' + query

        results = await self.bot.lavalink.get_tracks(query)

        if not results or not results['tracks']:
            return await ctx.send('Nothing found')

        tracks = results['tracks'][:10]  # First 10 results

        o = ''
        for i, t in enumerate(tracks, start=1):
            o += f'`{i}.` [{t["info"]["title"]}]({t["info"]["uri"]})\n'

        embed = discord.Embed(colour=ctx.guild.me.top_role.colour,
                              description=o)

        embed.timestamp = datetime.datetime.utcnow()
        await ctx.send(embed=embed)

    @commands.command(aliases=['dc', 'disconnect'])
    async def leave(self, ctx):
        """Disconnects from the voice channel."""
        player = self.bot.lavalink.players.get(ctx.guild.id)

        if not player.is_connected:
            return await ctx.send('Not connected.')

        if not ctx.author.voice or (player.is_connected and ctx.author.voice.channel.id != int(player.channel_id)):
            return await ctx.send('You\'re not in my voicechannel!')

        player.queue.clear()
        await player.disconnect()
        await ctx.send('*⃣ | Disconnected.')


def setup(bot):
    bot.add_cog(Music(bot))
