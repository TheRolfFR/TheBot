import discord

from .isbotinvocal import isBotInChannel
from settings import *

async def disconnectVocal(bot, message, command, args, voiceClient = None):
  """
  Usage : `{bot_prefix}disconnectVocal`
  Deconnecte le bot du vocal égal à l'utilisateur
  """
  if message.author.voice:
    # get my voice channel
    myChannel = message.author.voice.channel

    # get the members of the channel
    membersOfMyChannel = myChannel.members

    # check if I am in the channel
    meMember = await isBotInChannel(bot, myChannel)

    if not (voiceClient is None):
      await voiceClient.disconnect()
      return 

    # if i am in the channel then i am kicking myself (used to solve the disconnecting bot issue)
    if meMember != None:
      await message.channel.send("*Déconnexion depuis " + myChannel.name + "*")
      try:
        await meMember.kick()
      except discord.Forbidden as fbd:
        await message.channel.send(embed=discord.Embed(color=ERROR_COLOR, description=f":x: Le bot n'a pas la permission de kick des membres :x:"))