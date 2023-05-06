import discord
import asyncio

from settings import *

import json
import youtube_dl

import os
from commands.player import PlayerList, PlayerSource, Player
import re

import time
from utility import convert_dhms_string

regexp_youtube_url = re.compile(
    r"""^(https?\:\/\/)?(www\.)?(youtube\.com|youtu\.?be)\/.+$""", re.IGNORECASE
)

ytdl_format_options = {"format": "bestaudio"}

ffmpeg_options = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
}

ydl = youtube_dl.YoutubeDL(ytdl_format_options)


class YouTubeSource(PlayerSource):
    _source: discord.AudioSource
    _queue: list
    _player: Player
    _loop: asyncio.AbstractEventLoop
    _duration: float
    _timestamp: float
    _diff: float

    def __init__(self, display_name: str, urls, loop: asyncio.AbstractEventLoop):
        self._loop = loop
        self._diff = 0
        self._timestamp = 0
        url = ""
        queue = []

        if isinstance(urls, str):
            url = urls
        elif isinstance(urls, list):
            url = urls[0]
            queue = urls[1:]

        super().__init__(display_name, url)
        self._player = None
        self._queue = queue

    async def load(self):
        (url2, duration, name) = await YouTubeSource.from_url(self.path)
        self._source = await discord.FFmpegOpusAudio.from_probe(url2, **ffmpeg_options)
        self._duration = duration
        self.display_name = name  # update name too

    @classmethod
    async def from_url(cls, url):
        info = ydl.extract_info(url, download=False)

        return (
            info["formats"][0]["url"],
            info["duration"],
            f"{info['title']} ({convert_dhms_string(info['duration'])})",
        )

    def source(self):
        self._timestamp = time.time()
        self._diff = 0
        return self._source

    def after(self, player: Player):
        self._diff += time.time() - self._timestamp
        self._timestamp = -1
        if self._player is None:
            self._player = player

        return self.nextsong

    def duration(self):
        return self._duration

    def progress(self):
        return (
            round(self._diff, 0)
            if self._timestamp == -1
            else round(self._diff + time.time() - self._timestamp, 0)
        )

    def on_pause(self):
        now = time.time()
        super().on_pause()
        self._diff += now - self._timestamp
        self._timestamp = -1

    def on_resume(self):
        self._timestamp = time.time()
        super().on_resume()

    def nextsong(self, error):
        if error is not None or len(self._queue) == 0:
            return

        next = self._queue.pop(0)

        fut = asyncio.run_coroutine_threadsafe(
            self._player.stop(disconnect=False), self._loop
        )

        try:
            fut.result()
            self.path = next
            fut = asyncio.run_coroutine_threadsafe(self.load(), self._loop)
            fut.result()
            coro = self._player.play(self)
            fut = asyncio.run_coroutine_threadsafe(coro, self._loop)
            fut.result()
        except:
            # an error happened
            pass

    def enqueue(self, url):
        if isinstance(url, str):
            self._queue.append(url)
        elif isinstance(url, list):
            self._queue += url

    def clear(self):
        self._queue.clear()


CMD_YOUTUBE_NAME = "youtube"


async def cmd_youtube(
    bot: discord.Client,
    message: discord.Message,
    command: str,
    args: list,
    voicePlayers: PlayerList,
):
    """
    Joue une vidéo YouTube dans le channel audio
    `{bot_prefix}youtube play <url>` : Joue une vidéo
    `{bot_prefix}youtube skip` : Joue une vidéo
    `{bot_prefix}youtube clear` : Joue une vidéo
    `{bot_prefix}youtube playing` : Indique quelle vidéo est jouée
    `{bot_prefix}youtube queue` : Indique quelles vidéos sont en attente
    `{bot_prefix}youtube pause`: Met en pause la vidéo
    `{bot_prefix}youtube resume` : Rejoue la vidéo
    `{bot_prefix}youtube stop` : Stoppe la vidéo
    """

    # nope need url
    if not args:
        await message.channel.send(
            embed=discord.Embed(
                title=":x: Erreur de commande",
                color=ERROR_COLOR,
                description=f"Allez voir l'aide avec {bot.prefix}help {CMD_YOUTUBE_NAME}",
            ),
            reference=message,
            mention_author=False,
        )
        return

    player = voicePlayers.get_player(message.guild)

    if (
        isinstance(args, list) and len(args) == 1
    ):  # pause resume or stop (actions while playing)
        # extract action
        action = args[0]

        # do action
        if action == "playing":
            msg = "Rien n'est joué actuellement"

            emb = discord.Embed(
                title="YouTube",
                color=CONFIRM_COLOR,
                description=msg,
            )

            if player.is_playing() or player.is_paused():
                name = player.name()
                channel_name = player.channel_name()
                if name:
                    if player.is_paused():
                        msg = f"``{ name }`` pausée dans ``{ channel_name }``"
                    else:
                        msg = f"``{ name }`` jouée dans ``{ channel_name }``"
                    emb.description = msg

                if isinstance(player.source, YouTubeSource):
                    progress = player.source.progress()
                    duration = player.source.duration()

                    if progress > duration:
                        progress = duration

                    emb.add_field(
                        name="Time",
                        value=f"[{convert_dhms_string(progress)} / {convert_dhms_string(duration)}]",
                    )

                    percent = (progress / duration) * 100 // 1
                    index = min(percent // 10, 9)
                    value = ""
                    for i in range(0, 10):
                        value += "―" if i != index else "▬"
                    value += f" **{percent}**%"
                    emb.add_field(name="Progress", value=value)

            await message.channel.send(
                embed=emb, reference=message, mention_author=False
            )
            return

        elif action == "queue":
            if isinstance(player.source, YouTubeSource):
                queue_length = len(player.source._queue)

                desc_list = []
                for url in player.source._queue:
                    infos = await YouTubeSource.from_url(url)
                    desc_list.append(f"**[{infos[2]}]({url})**")

                desc = (
                    f"{queue_length} vidéo{'s' if queue_length > 1 else ''} en attente"
                )

                if queue_length > 0:
                    desc += ":\n"
                    desc += "\n".join(desc_list)

                await message.channel.send(
                    embed=discord.Embed(
                        title="Youtube: queue",
                        color=CONFIRM_COLOR,
                        description=desc[:2048],
                    ),
                    reference=message,
                    mention_author=False,
                )
            return

        elif action == "clear":
            if isinstance(player.source, YouTubeSource):
                player.source.clear()
                await message.channel.send(
                    embed=discord.Embed(
                        title="YouTube",
                        color=CONFIRM_COLOR,
                        description="Queue cleared",
                    ),
                    reference=message,
                    mention_author=False,
                )
            return

        # stop if not in channel with bot

        # if user not in voice channel
        if not message.author.voice:
            return

        # if bot not in voice channel
        if not message.guild.voice_client:
            return

        # if bot not in same voice channel
        if message.guild.voice_client.channel != message.author.voice.channel:
            return

        if action == "pause":
            player.pause()
            await message.add_reaction("⏸️")
        elif action == "resume":
            player.resume()
            await message.add_reaction("▶️")
        elif action == "stop":
            await player.stop()
            await message.add_reaction("⏹️")
        elif action == "skip":
            if isinstance(player.source, YouTubeSource):
                player.source.nextsong(None)
                await message.add_reaction("⏭️")
            return

        # exit da fuck outa here
        return

    if isinstance(args, list) and (args[0] == "play" or len(args) == 2):
        if args[0] == "play":  # play a radio
            # get url word
            supposed_urls = args[1:]

            urls = []

            for url in supposed_urls:
                res = re.match(regexp_youtube_url, url)
                if res is not None:
                    urls.append(url)

            # exit if user not in voice channel
            if not message.author.voice:
                error = await message.channel.send(
                    embed=discord.Embed(
                        color=ERROR_COLOR,
                        description=message.author.mention
                        + ", tu n'es pas dans un channel audio.",
                    ),
                    reference=message,
                )
                await asyncio.sleep(2)
                await error.delete()
                return

            await message.add_reaction("⏳")

            # go to voice channel
            await player.go_to(message.author.voice.channel)

            read = True

            if (
                player.is_playing()
                and player.source is not None
                and isinstance(player.source, YouTubeSource)
            ):
                read = False
                player.source.enqueue(urls)
            else:
                youtube_source = YouTubeSource("YouTube", urls, bot.loop)
                await youtube_source.load()
                await player.play(youtube_source)

            await message.remove_reaction("⏳", bot.user)

            await message.channel.send(
                embed=discord.Embed(
                    title="YouTube",
                    color=CONFIRM_COLOR,
                    description=f'{len(urls)} titre{"s" if len(urls) > 1 else "" } dans ``{ player.channel_name() }``\n Démarrage de ``{player.name()}``...'
                    if read
                    else f"Ajout de {len(urls)} titre{'s' if len(urls) > 1 else '' } à la queue",
                ),
                reference=message,
                mention_author=False,
            )
