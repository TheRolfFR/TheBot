import discord
import asyncio
import re

from settings import *
from commands.mod.guild_settings import GuildSettingGroup

RENAME_SETTING_NAME = "rename"
RENAME_SETTING_NAME_SET = "set"
RENAME_SETTING_TYPE_SET = dict
RENAME_SETTINGE_DEFAULT_SET = {}
RENAME_SETTING_NAME_ORIGINAL = "original"
RENAME_SETTING_TYPE_ORIGINAL = dict
RENAME_SETTINGE_DEFAULT_ORIGINAL = {}

renameSettings = None
renameEnableItem = None
renameOriginalItem = None

def getRenameSettings(message: discord.Message):
  global renameSettings, renameEnableItem, renameOriginalItem

  if renameSettings is not None:
    return

  # load global rename settings
  renameSettings = GuildSettingGroup(message.guild.id, RENAME_SETTING_NAME)

  # get rename enable item
  renameEnableItem = renameSettings.create_item(RENAME_SETTING_NAME_SET, RENAME_SETTING_TYPE_SET, RENAME_SETTINGE_DEFAULT_SET)

  # get rename original item
  renameOriginalItem = renameSettings.create_item(RENAME_SETTING_NAME_ORIGINAL, RENAME_SETTING_TYPE_ORIGINAL, RENAME_SETTINGE_DEFAULT_ORIGINAL)

INDEX_CHANGE = 0
INDEX_RESET = 1
INDEX_SET = 2
INDEX_ORIGINAL = 3


async def cmd_rename(bot: discord.Client, message: discord.Message, command: str, args: list):
  """
  `{bot_prefix}rename change "<nouveauNom>"` : change le nom du canal actuel (limité à 2x toutes les 10min)
  `{bot_prefix}rename reset "<channel>"` : change le nom du channel "<channel>" à sno nom original (limité à 2x toutes les 10min)
  `{bot_prefix}rename set "<channel>" <0|1>` : autorise ou non le renommage de channel vocal du nom donné
  `{bot_prefix}rename original "<channel>"` : met à jour le nom original du channel (remis quand plus personne dans le channel)
  """
  argstring = " ".join(args)

  arr = [
    re.compile('change "(.+)"').match(argstring),
    re.compile('reset "(.+)"').match(argstring),
    re.compile('set "(.+)" (0|1)').match(argstring),
    re.compile('original "(.+)"').match(argstring)
  ]

  allNone = True
  value = None
  i = 0
  while i < len(arr) and allNone:
    if arr[i] is not None:
      allNone = False
      value = arr[i].group(1)
    i += 1

  if allNone:
    return

  # change command
  if arr[INDEX_CHANGE] is not None:
    if not message.author.voice:
      error = await message.channel.send(
          embed=discord.Embed(
              color=ERROR_COLOR,
              description=message.author.mention + "Vous n'êtes pas en en vocal",
          )
      )
      await asyncio.sleep(2)
      await error.delete()
      return

    # load global rename settings
    getRenameSettings(message)

    try:
      # rename must be authorised
      if not renameEnableItem.value[str(message.author.voice.channel.id)]:
        raise Exception("not authorized")
      
      # else it is
      done = await message.channel.send(embed=discord.Embed(
        title=":speaker: Rename channel",
        color=CONFIRM_COLOR,
        description="Nom changé :white_check_mark:"
      ))
      await asyncio.sleep(2)
      await done.delete()

      await message.author.voice.channel.edit(name=value, reason="TheBot renommage par " + message.author.name)
    except BaseException as e:
      error = await message.channel.send(
          embed=discord.Embed(
              color=ERROR_COLOR,
              description=message.author.mention + "Renommage interdit",
          )
      )
      await asyncio.sleep(2)
      await error.delete()
      raise e
    return

  # else I need to find the channel by its name
  channelList = message.guild.voice_channels
  foundChannel = None
  i = 0
  while i < len(channelList) and foundChannel is None:
    if channelList[i].name == value:
      foundChannel = channelList[i]
    i += 1

  if foundChannel is None:
    return

  # reset to original name
  if arr[INDEX_RESET] is not None:
    getRenameSettings(message)
    if str(foundChannel.id) in renameOriginalItem.value:
      try:
        # else it is
        done = await message.channel.send(embed=discord.Embed(
          title=":speaker: Rename channel",
          color=CONFIRM_COLOR,
          description="Nom réinitialisé :white_check_mark:"
        ))
        await asyncio.sleep(2)
        await done.delete()

        await message.author.voice.channel.edit(name=renameOriginalItem.value[str(foundChannel.id)], reason="TheBot renommage par " + message.author.name)
      except BaseException as e:
        error = await message.channel.send(
            embed=discord.Embed(
                color=ERROR_COLOR,
                description=message.author.mention + "Renommage interdit",
            )
        )
        await asyncio.sleep(2)
        await error.delete()
        raise e
    return

  if arr[INDEX_ORIGINAL] is not None:
    getRenameSettings(message)
    val = renameOriginalItem.value
    val[str(foundChannel.id)] = foundChannel.name
    renameSettings.save()

    changed = await message.channel.send(embed=discord.Embed(
      title=":speaker: Rename channel",
      color=CONFIRM_COLOR,
      description="Nom original sauvegardé :white_check_mark:"
    ))
    await asyncio.sleep(2)
    await changed.delete()
    return
  
  # else set command
  if not message.author.guild_permissions.administrator:
    await message.channel.send(embed=discord.Embed(
      title=":speaker: Rename channel",
      color=ERROR_COLOR,
      description=":x: vous n'avez pas la permission de faire ça, vous devez être admin :x:"
    ))
    return

  getRenameSettings(message)
  print(arr[INDEX_SET].groups())
  renameEnableItem.value[str(foundChannel.id)] = arr[INDEX_SET].group(2) == "1"

  renameSettings.save()
  changed = await message.channel.send(embed=discord.Embed(
    title=":speaker: Rename channel",
    color=CONFIRM_COLOR,
    description="Paramètre sauvegardé :white_check_mark:"
  ))
  await asyncio.sleep(2)
  await changed.delete()
  return