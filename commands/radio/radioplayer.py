import discord
import asyncio

from commands.radio.radiodescription import RadioDescription
import commands.radio.radiolist as rl

class RadioPlayer:
  """Radio player for one guild"""
  vc: discord.VoiceClient = None
  radio: RadioDescription = None
  guild: discord.Guild = None

  def __init__(self, guild: discord.Guild):
    self.guild = guild
  
  async def go_to(self, channel: discord.VoiceChannel):
    """Connect or move to another channel"""

    # connect if no voice channel
    if self.vc is None or channel.guild.voice_client is None:
      self.vc = await channel.connect() # timeout=10
    else:
      # else check if not good channel then move
      if self.vc.channel != channel:
        self.vc.move_to(channel)
  
  async def play(self, radio: RadioDescription):
    """Start playing radio in current channel"""
    if self.radio is None or self.radio != radio:
      self.radio = radio
      
      if self.vc is None:
        raise AttributeError("Radio player must have a voice client, please use go_to function")

      # stop if playing
      if self.vc.is_playing():
        self.vc.stop()

      # replay
      self.vc.play(discord.FFmpegPCMAudio(source=self.radio.url))
    return
  
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
      self.radio = None

  def is_playing(self):
    """Tells if radio playing or not"""
    return self.vc is not None and self.vc.is_playing()

  def is_paused(self):
    return self.vc.is_paused()

  def radio_name(self):
    """Tells what radio playing if playing else False"""
    if not isinstance(self.vc, discord.VoiceProtocol):
      return False
    
    return self.radio.display_name

  def channel_name(self):
    """Tells where radio playing if playing else False"""
    if not isinstance(self.vc, discord.VoiceProtocol):
      return False
    
    return self.vc.channel.name