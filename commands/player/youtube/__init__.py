import discord
import asyncio

from settings import *

import json
import youtube_dl

import os
from commands.player import PlayerList, PlayerSource, Player
import re

regexp_youtube_url = re.compile(r"""^(https?\:\/\/)?(www\.)?(youtube\.com|youtu\.?be)\/.+$""", re.IGNORECASE)

ytdl_format_options = {
  'format': 'bestaudio'
}

ffmpeg_options = {
  'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
  'options': '-vn'
}

ydl = youtube_dl.YoutubeDL(ytdl_format_options)

class YouTubeSource(PlayerSource):
  _source: discord.AudioSource
  _queue: list
  _player: Player
  _loop: asyncio.AbstractEventLoop
  def __init__(self, display_name: str, urls, loop: asyncio.AbstractEventLoop):
    self._loop = loop
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
    (url2, name) = await YouTubeSource.from_url(self.path)
    self._source = await discord.FFmpegOpusAudio.from_probe(url2, **ffmpeg_options)
    self.display_name = name # update name too

  @classmethod
  async def from_url(cls, url):
    info = ydl.extract_info(url, download=False)

    return (info['formats'][0]['url'], f"{info['title']} ({ '{:d}:{:02d}:{:02d}'.format(info['duration']//3600, info['duration']//60, info['duration']%60) if info['duration'] > 3600 else '{:d}:{:02d}'.format(info['duration']//60, info['duration']%60) })")
  
  def source(self):
    return self._source

  def after(self, player: Player):
    if self._player is None:
      self._player = player
    
    return self.nextsong

  def nextsong(self, error):
    if error is not None or len(self._queue) == 0:
      return
    
    next = self._queue.pop(0)

    self.path = next
    fut = asyncio.run_coroutine_threadsafe(self.load(), self._loop)
    try:
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

async def cmd_youtube(bot: discord.Client, message: discord.Message, command: str, args: list, voicePlayers: PlayerList):
    """
    Joue une vidéo YouTube dans le channel audio
    `{bot_prefix}youtube play <url>` : Joue une vidéo
    `{bot_prefix}youtube playing` : Indique quelle vidéo est jouée
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
        mention_author=False
      )
      return
    
    player = voicePlayers.get_player(message.guild)

    if isinstance(args, list) and len(args) == 1: # pause resume or stop (actions while playing)
        # extract action
        action = args[0]

        # do action
        if action == 'playing':
            msg = "Rien n'est joué actuellement"

            radio_name = player.name()
            channel_name = player.channel_name()
            if radio_name:
                if player.is_paused():
                    msg = f'``{ radio_name }`` pausée dans ``{ channel_name }``'
                else:
                    msg = f'``{ radio_name }`` jouée dans ``{ channel_name }``'
            
            await message.channel.send(
              embed=discord.Embed(
                title="YouTube",
                color=CONFIRM_COLOR,
                description=msg,
              ),
              reference=message,
              mention_author=False
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
        
        if action == 'pause':
            player.pause()
            await message.add_reaction('⏸️')
        elif action == 'resume':
            player.resume()
            await message.add_reaction('▶️')
        elif action == 'stop':
            await player.stop()
            await message.add_reaction('⏹️')
        
        #exit da fuck outa here
        return

    if isinstance(args, list) and (args[0] == 'play' or len(args) == 2):
        if args[0] == 'play': # play a radio
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
                      description=message.author.mention + ", tu n'es pas dans un channel audio.",
                  ),
                  reference=message
              )
              await asyncio.sleep(2)
              await error.delete()
              return

          await message.add_reaction('⏳')

          # go to voice channel
          await player.go_to(message.author.voice.channel)

          read = True

          if player.is_playing() and player.source is not None and isinstance(player.source, YouTubeSource):
            read = False
            player.source.enqueue(urls)
          else:
            youtube_source = YouTubeSource("YouTube", urls, bot.loop)
            await youtube_source.load()
            await player.play(youtube_source)

          await message.remove_reaction('⏳', bot.user)

          await message.channel.send(
            embed=discord.Embed(
              title="YouTube",
              color=CONFIRM_COLOR,
              description=f'{len(urls)} titre{"s" if len(urls) > 1 else "" } dans ``{ player.channel_name() }``\n Démarrage de ``{player.name()}``...' if read else f"Ajout de {len(urls)} titre{'s' if len(urls) > 1 else '' } à la queue"
            ),
            reference=message,
            mention_author=False
          )