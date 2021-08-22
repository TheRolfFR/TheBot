import discord
import asyncio

from commands.player.playersource import *

class PlayerList:
  def __init__(self):
    self.players = []
    pass

  def get_player(self, guild: discord.Guild):
    """Get or create player for guild"""
    result = None
    i = 0
    while i < len(self.players) and result is None:
        if self.players[i].guild == guild:
            result = self.players[i]
        
        i += 1

    """No result found, create"""
    if result is None:
        result = Player(guild=guild)
        self.players.append(result)
    
    return result

  async def update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
    # check if not joined
    if before.channel is None:
        return

    # check if multiple persons after or if if no one now
    if len(before.channel.members) > 1 or len(before.channel.members) == 0:
        return

    # check if the only member left in channel is the bot :,(
    if before.channel.members[0] != before.channel.guild.me:
        return

    # check if player in guild
    player = None
    i = 0
    while i < len(self.players) and player is None:
        if self.players[i].guild == before.channel.guild:
            player = self.players[i]
        
        i += 1
    
    if player is None:
        return
        
    print("Radio player auto disconnecting from " + before.channel.name + " because empty room...")
    await player.stop()

class Player:
  """Radio player for one guild"""
  vc: discord.VoiceClient = None
  source: PlayerSource = None
  guild: discord.Guild = None
  volume: float

  def __init__(self, guild: discord.Guild):
    self.guild = guild
    self.volume = 100
  
  async def go_to(self, channel: discord.VoiceChannel):
    """Connect or move to another channel"""

    # connect if no voice channel
    if self.vc is None or channel.guild.voice_client is None:
      self.vc = await channel.connect() # timeout=10
    else:
      # else check if not good channel then move
      if self.vc.channel != channel:
        self.vc.move_to(channel)
  
  async def play(self, source: PlayerSource):
    """Start playing radio in current channel"""
    if self.source is None or self.source != source:
      self.source = source
      
      if self.vc is None:
        raise AttributeError("Player must have a voice client, please use go_to function")

      # stop if playing
      if self.vc.is_playing():
        self.vc.stop()

      # replay
      self.vc.play(source.source())
      self.vc.source = discord.PCMVolumeTransformer(self.vc.source)
    return

  def setVolume(self, volume):
    """Changes radio volume"""
    try:
      val = float(volume)

      if val < 0.0 or val > 100.0:
        return False
    except:
      return False

    self.volume = val
    self.vc.source.volume = self.volume / 100.0

    return True
  
  def pause(self):
    """Pause play of radio"""
    if self.vc is not None and not self.vc.is_paused():
      self.vc.pause()
  
  def resume(self):
    """Resume play of radio"""
    if self.vc is not None and self.vc.is_paused():
      self.vc.resume()

  async def stop(self):
    """Stop radio playback and disconnect"""
    if self.vc is not None:
      if self.vc.is_playing():
        self.vc.stop()

      await self.vc.disconnect()

      self.vc = None
      self.source = None

  def is_playing(self):
    """Tells if radio playing or not"""
    return self.vc is not None and self.vc.is_playing()

  def is_paused(self):
    return self.vc.is_paused()

  def name(self):
    """Tells what radio playing if playing else False"""
    if not isinstance(self.vc, discord.VoiceProtocol):
      return False
    
    return self.source.display_name

  def channel_name(self):
    """Tells where radio playing if playing else False"""
    if not isinstance(self.vc, discord.VoiceProtocol):
      return False
    
    return self.vc.channel.name