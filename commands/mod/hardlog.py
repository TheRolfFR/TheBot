import discord
import asyncio
from os.path import abspath, join, dirname
from settings import *
import commands.mod.guild_settings as guild_settings

HARDLOG_KEY = 'hardlog'

HARDLOG_KEY_CHANNEL_ID = 'channel_id'
HARDLOG_KEY_CHANNEL_ID_DEFAULT_VALUE = None

HARDLOG_KEY_ENABLED = 'enabled'
HARDLOG_KEY_ENABLED_DEFAULT_VALUE = True

HARDLOG_KEY_ENABLED_DELETE = 'enabled_delete'
HARDLOG_KEY_ENABLED_DELETE_DEFAULT_VALUE = True

HARDLOG_KEY_ENABLED_EDIT = 'enabled_edit'
HARDLOG_KEY_ENABLED_EDIT_DEFAULT_VALUE = True

HARDLOG_DEFAULT_VALUE_ENABLED = True
class HardlogSettings:
  guild_id: int
  channel_id: int
  enabled: bool
  enabled_delete: bool
  enabled_edit: bool

  """Class used to store hardlog settings"""
  def __init__(self, guild_id: int):
    # save guild_id
    self.guild_id = guild_id

    # get settings
    hardlog_settings = guild_settings.get_setting(guild_id, HARDLOG_KEY)

    if hardlog_settings is None or not isinstance(hardlog_settings, dict):
      hardlog_settings = {}

    if HARDLOG_KEY_CHANNEL_ID in hardlog_settings:
      self.channel_id = hardlog_settings[HARDLOG_KEY_CHANNEL_ID]
    else:
      self.channel_id = HARDLOG_KEY_CHANNEL_ID_DEFAULT_VALUE

    if HARDLOG_KEY_ENABLED in hardlog_settings:
      self.enabled = hardlog_settings[HARDLOG_KEY_ENABLED]
    else:
      self.enabled = HARDLOG_KEY_ENABLED_DEFAULT_VALUE

    if HARDLOG_KEY_ENABLED_DELETE in hardlog_settings:
      self.enabled_delete = hardlog_settings[HARDLOG_KEY_ENABLED_DELETE]
    else:
      self.enabled_delete = HARDLOG_KEY_ENABLED_DELETE_DEFAULT_VALUE

    if HARDLOG_KEY_ENABLED_EDIT in hardlog_settings:
      self.enabled_edit = hardlog_settings[HARDLOG_KEY_ENABLED_EDIT]
    else:
      self.enabled_edit = HARDLOG_KEY_ENABLED_EDIT_DEFAULT_VALUE

  def save(self):
    hardlog_settings = {}
    hardlog_settings[HARDLOG_KEY_CHANNEL_ID] = self.channel_id
    hardlog_settings[HARDLOG_KEY_ENABLED] = self.enabled
    hardlog_settings[HARDLOG_KEY_ENABLED_DELETE] = self.enabled_delete
    hardlog_settings[HARDLOG_KEY_ENABLED_EDIT] = self.enabled_edit
    
    guild_settings.set_setting(self.guild_id, HARDLOG_KEY, hardlog_settings)
  
  def enable(self, state: bool):
    self.enabled = state
    self.save()

  def enable_delete(self, state: bool):
    self.enabled_delete = state
    self.save()

  def enable_edit(self, state: bool):
    self.enabled_edit = state
    self.save()

  def here(self, channel_id: int):
    self.channel_id = channel_id
    self.save()

  def __eq__(self, o):
    """== operator overload"""
    if isinstance(o, int):
      return o == self.guild_id

    return False

hardlog_settings_list = []

def get_hardlog_settings(guild_id: int):
  """Get or create hardlog settings"""
  i = 0
  while i < len(hardlog_settings_list):
    if hardlog_settings_list[i] == guild_id:
      return hardlog_settings_list[i]

    i += 1

  # else it was not so find it or create it
  res = HardlogSettings(guild_id)
  hardlog_settings_list.append(res)

  return res

async def cmd_hardlog(bot: discord.Client, message: discord.Message, command: str, args: list):
  """
  `{bot_prefix}hardlog here` : change le lieu de hardlog
  `{bot_prefix}hardlog disable` : désactive le hardlog
  `{bot_prefix}hardlog disable [edit|delete]` : désactive certains hardlog
  `{bot_prefix}hardlog enable` : active le hardlog
  `{bot_prefix}hardlog disable [edit|delete]` : active certains hardlog
  """

  # get da fuck outa here if no args
  if len(args) <= 0:
    return

  # you gotta be an admin
  if not message.author.guild_permissions.administrator:
    await message.channel.send(embed=discord.Embed(
      title=":notepad_spiral: Hardlog",
      color=ERROR_COLOR,
      description=":x: vous n'avez pas la permission de faire ça, vous devez être admin :x:"
    ))
    return

  # one arguments
  if len(args) == 1 and args[0] in ['here', 'enable', 'disable']:
    # get guild id
    guild_id = message.channel.guild.id

    # get settings
    guild_hardlog_settings = get_hardlog_settings(guild_id)

    cmd = args[0]

    if cmd == 'here':
      guild_hardlog_settings.here(message.channel.id)
    else:
      state = True if args[0] == 'enable' else False
      guild_hardlog_settings.enable(state)

    await message.channel.send(embed=discord.Embed(
      title=":notepad_spiral: Hardlog",
      color=CONFIRM_COLOR,
      description="Paramètre sauvegardé :white_check_mark:"
    ))
  
  elif len(args) == 2 and args[0] in ['enable', 'disable'] and args[1] in ['edit', 'delete']:
    # get guild id
    guild_id = message.channel.guild.id

    # get settings
    guild_hardlog_settings = get_hardlog_settings(guild_id)

    # get state
    state = True if args[0] == 'enable' else False

    if args[1] == 'edit':
      guild_hardlog_settings.enable_edit(state)
    else:
      guild_hardlog_settings.enable_delete(state)

    await message.channel.send(embed=discord.Embed(
      title=":notepad_spiral: Hardlog",
      color=CONFIRM_COLOR,
      description="Paramètre sauvegardé :white_check_mark:"
    ))

async def cmd_hardlog_update(bot: discord.Client ,message_original: discord.Message, message_edite: any, edit=False, delete=False):
  # bruh the two are True or False, not what I want
  if edit == delete:
    return

  guild = message_original.channel.guild

  # this is a guild message listener
  if guild is None:
    return

  guild_id = guild.id

  # if message is not from me
  if message_original.author == guild.me:
    return

  guild_hardlog_settings = get_hardlog_settings(guild_id)

  # if no channel defined then no thanks
  if guild_hardlog_settings.channel_id is None:
    return

  # get the channel now ?
  hardlog_channel = bot.get_channel(guild_hardlog_settings.channel_id)

  # get out if this channel doesn't exist
  if hardlog_channel is None:
    return

  # do it only if enabled
  if not guild_hardlog_settings.enabled:
    return

  if delete == True and not guild_hardlog_settings.enabled_delete:
    return

  if edit == True and not guild_hardlog_settings.enabled_edit:
    return

  status = "Supprimé" if delete == True else "Édité"

  desc = ""
  if delete:
    desc = message_original.content
  else:
    desc = f"{ message_original.content } -> { message_edite.content }"
  await hardlog_channel.send(embed=discord.Embed(
    title = f":notepad_spiral: Hardlog: message { status } de { message_original.author.name }",
    color = CONFIRM_COLOR,
    description=desc
  ))