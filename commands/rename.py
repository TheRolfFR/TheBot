import discord
import asyncio

from settings import *
from commands.mod.guild_settings import GuildSettingGroup

RENAME_SETTING_NAME = "rename"
RENAME_SETTING_NAME_SET = "set"
RENAME_SETTING_TYPE_SET = dict
RENAME_SETTINGE_DEFAULT_SET = {}

renameSettings = None
renameEnableItem = None

def getRenameSettings(message: discord.Message):
  global renameSettings, renameEnableItem

  if renameSettings is not None:
    return

  # load global rename settings
  renameSettings = GuildSettingGroup(message.guild.id, RENAME_SETTING_NAME)

  # get rename enable item
  renameEnableItem = renameSettings.create_item(RENAME_SETTING_NAME_SET, RENAME_SETTING_TYPE_SET, RENAME_SETTINGE_DEFAULT_SET)


async def cmd_rename(bot: discord.Client, message: discord.Message, command: str, args: list):
  """
  `{bot_prefix}rename set <0|1>` : autorise ou non le renommage de channel vocal actuel
  `{bot_prefix}rename change <nouveauNom>` : change le nom (limité à 2x toutes les 10min)
  """

  # if user not in voice channel
  if not message.author.voice:
      return

  # verify subcommand
  subCommand = args[0].lower()
  value = " ".join(args[1:])
  if subCommand != "set" and subCommand != "change":
    error = await message.channel.send(
        embed=discord.Embed(
            color=ERROR_COLOR,
            description=message.author.mention + " Vous devez mettre comme commande change ou set",
        )
    )
    await asyncio.sleep(2)
    await error.delete()
    return

  if subCommand == "set":
    if isinstance(args, list) and len(args) != 2:
      error = await message.channel.send(
          embed=discord.Embed(
              color=ERROR_COLOR,
              description=message.author.mention + " Nombre incorrect d'arguments",
          )
      )
      await asyncio.sleep(2)
      await error.delete()
      return

    getRenameSettings(message)
    renameEnableItem.value[str(message.author.voice.channel.id)] = value == "1"

    renameSettings.save()
    changed = await message.channel.send(embed=discord.Embed(
      title=":speaker: Rename channel",
      color=CONFIRM_COLOR,
      description="Paramètre sauvegardé :white_check_mark:"
    ))
    await asyncio.sleep(2)
    await changed.delete()
    return
  else:
    if isinstance(args, list) and len(args) < 2:
      error = await message.channel.send(
          embed=discord.Embed(
              color=ERROR_COLOR,
              description=message.author.mention + " Nombre incorrect d'arguments",
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