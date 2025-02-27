import sys
import time
import os
import logging

import discord
import asyncio
from yt_dlp.version import __version__ as ytdl_version
from yt_dlp import YoutubeDL

from commands.player import PlayerSource, Player
from utility import convert_dhms_string

ffmpeg_options = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
}

ytdl_format_options = {
    'verbose': os.getenv("DEV", "false").lower() == "true",
    'no_warnings': True,
    'format': 'bestaudio[ext=webm]/bestaudio',
    'noplaylist': True,
    'extractor_args': {'youtube': {'player_client': ['web_innertube']}}
}
ydl = YoutubeDL(ytdl_format_options)

log = logging.getLogger(__name__)

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
        log.debug(f"Queue size is now {len(self._queue)}")

    async def load(self):
        res = YouTubeSource.from_url(self.path)
        if res is None:
            return None

        (url2, duration, name) = res
        self._source = await discord.FFmpegOpusAudio.from_probe(url2, **ffmpeg_options)
        self._duration = duration
        self.display_name = name  # update name too
        return name

    @classmethod
    def from_url(cls, url):
        res = None
        try:
            info = ydl.extract_info(url, download=False)

            res = (
                info["url"],
                info["duration"],
                f"{info['title']} ({convert_dhms_string(info['duration'])})",
            )
            log.info(res)
        except Exception as e:
            log.error(f"youtube-dl v{ytdl_version}", file=sys.stderr)
            log.error(e.__str__(), file=sys.stderr)
        return res

    def source(self):
        self._timestamp = time.time()
        self._diff = 0
        return self._source

    def after(self, player: Player):
        self._diff += time.time() - self._timestamp
        self._timestamp = -1
        if self._player is None:
            self._player = player

        def sync_nextsong(error):
            print("Starting YT item")
            asyncio.run_coroutine_threadsafe(self.nextsong(error), self._loop)
        return sync_nextsong

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

    async def nextsong(self, error):
        if error is not None or len(self._queue) == 0:
            return


        await self._player.stop(disconnect=False)

        nextsong = self._queue.pop(0)
        log.debug(f"Queue size is now {len(self._queue)}")
        self.path = nextsong

        load_name = await self.load()
        if load_name is not None:
            await self._player.play(self)


    async def enqueue(self, url):

        if isinstance(url, str):
            res = YouTubeSource.from_url(url)
            if res is not None:
                self._queue.append(url)
                return res
        elif isinstance(url, list):
            for u in url:
                res = YouTubeSource.from_url(u)
                if res is None:
                    return None
            self._queue += url
        log.debug(f"Queue size is now {len(self._queue)}")

    def clear(self):
        self._queue.clear()
        log.debug(f"Queue size is now {len(self._queue)}")