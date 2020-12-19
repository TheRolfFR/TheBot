import discord
import asyncio
import commands.mod.guild_settings as guild_settings
from settings import *
from .instant_vocal_channel import InstantVocalManager

IV_KEY = 'instant_vocal'

IV_LOBBY_ID_KEY = 'lobby_channel_id'
IV_LOBBY_ID_KEY_DEFAULT = None

IV_VOICE_CATEGORY_ID_KEY = 'vocals_category_id'
IV_VOICE_CATEGORY_ID_KEY_DEFAULT = None

IV_VOICE_CHANNEL_LIST_KEY = 'vocals_list'
IV_VOICE_CHANNEL_LIST_KEY_DEFAULT = []

class InstantVoiceSettings(guild_settings.GuildSettingGroup):
  """Class used to store hardlog settings"""

  def __init__(self, guild_id: int):
    super().__init__(guild_id, IV_KEY)

    super().create_item(key=IV_LOBBY_ID_KEY,           item_type=int,  default=IV_LOBBY_ID_KEY_DEFAULT)
    super().create_item(key=IV_VOICE_CATEGORY_ID_KEY,  item_type=int,  default=IV_VOICE_CATEGORY_ID_KEY_DEFAULT)
    super().create_item(key=IV_VOICE_CHANNEL_LIST_KEY, item_type=list, default=IV_VOICE_CHANNEL_LIST_KEY_DEFAULT)

iv_settings_list = []

def get_instant_vocal_settings(guild_id: int):
  """Get or create instant voice settings"""
  i = 0
  while i < len(iv_settings_list):
    if iv_settings_list[i] == guild_id:
      return iv_settings_list[i]

    i += 1

  # else it was not so find it or create it
  res = InstantVoiceSettings(guild_id)
  iv_settings_list.append(res)

  return res

iv_guild_manager_list = []

def find_instant_vocal_manager(guild: discord.Guild):
  i = 0
  while i < len(iv_guild_manager_list) :
    if iv_guild_manager_list[i].guild_id() == guild.id:
      return iv_guild_manager_list[i]

    i += 1
  
  return None

async def get_instant_vocal_manager(guild: discord.Guild, category: discord.CategoryChannel, lobby: discord.VoiceChannel):
  """Get or create manager"""
  manager = find_instant_vocal_manager(guild)

  if manager != None:
    return manager

  guild_settings = get_instant_vocal_settings(guild.id)

  res = InstantVocalManager(guild=guild, category=category, lobby=lobby)
  try:
    await res.init(json_list=guild_settings.items[IV_VOICE_CHANNEL_LIST_KEY].value)
  except:
    pass

  iv_guild_manager_list.append(res)

  return res

async def cmd_instant_vocal(bot: discord.Client, message: discord.Message, command: str, args: list):
  """
  `{bot_prefix}instantVocal lobby <voiceChannelName>` Sets the voice channel <voiceChannelName> as the waiting lobby 
  `{bot_prefix}instantVocal category <CategoryName>` Sets the category <CategoryName> where bot creates the instant channels
  `{bot_prefix}instantVocal create "<VocalName>" [maxPlayers=0+]` Creates an instant vocal channel and places inside (can be 0 for unlimited)
  `{bot_prefix}instantVocal invite <@user1> <@user2>...` Moves users from lobby to the instant channel where I am
  """

  # all messages have at least 2 args
  if len(args) < 2:
    return

  # message must be from guild
  guild = message.channel.guild
  if guild is None:
    return

  # first arg must be supported
  if args[0] not in ['lobby', 'category', 'create', 'invite']:
    return

  guild_id = guild.id

  if args[0] == 'lobby':
    # get wanted lobby name
    lobby_name = ' '.join(args[1:])
    # first find vocal channel
    guild_channels = guild.channels
    channel_founds_name = [ ch for ch in guild_channels if (isinstance(ch, discord.VoiceChannel) and ch.name == lobby_name) ]

    print(channel_founds_name)

    if len(channel_founds_name) == 0:
      await message.channel.send(embed=discord.Embed(
        title="Ereur lors du changement du lobby Instant Vocal",
        description=f"Impossible de trouver le channel vocal `{ lobby_name }`",
        color=ERROR_COLOR
      ))
      return
    
    channel_found_id = channel_founds_name[0].id

    # then get settings, set value and save
    iv_settings = get_instant_vocal_settings(guild_id)
    iv_settings.items[IV_LOBBY_ID_KEY].value = channel_found_id
    iv_settings.save()

    await message.channel.send(embed=discord.Embed(
      title="Lobby Instant Vocal changé avec succès",
      description=f"Le lobby Instant Vocal est maintenant `{ lobby_name }`",
      color=CONFIRM_COLOR
    ))
    return
  
  if args[0] == 'category':
    category_name = ' '.join(args[1:]).upper()
    # first find vocal channel
    guild_channels = guild.channels
    channel_founds_name = [ ch for ch in guild_channels if (isinstance(ch, discord.CategoryChannel) and ch.name.upper() == category_name) ]

    if len(channel_founds_name) == 0:
      await message.channel.send(embed=discord.Embed(
        title="Ereur lors du changement de la catégorie Instant Vocal",
        description=f"Impossible de trouver la catégorie `{ category_name }`",
        color=ERROR_COLOR
      ))
      return
    
    channel_found_id = channel_founds_name[0].id

    # then get settings, set value and save
    iv_settings = get_instant_vocal_settings(guild_id)
    iv_settings.items[IV_VOICE_CATEGORY_ID_KEY].value = channel_found_id
    iv_settings.save()

    await message.channel.send(embed=discord.Embed(
      title="Catégorie Instant Vocal changée avec succès",
      description=f"La catégorie Instant Vocal est maintenant `{ category_name }`",
      color=CONFIRM_COLOR
    ))
    return
    
  iv_settings = get_instant_vocal_settings(guild_id)

  # exit if no lobby
  if iv_settings.items[IV_LOBBY_ID_KEY].value == IV_LOBBY_ID_KEY_DEFAULT:
    await message.channel.send(embed=discord.Embed(
      title="Paramètre introuvable",
      description="Impossible de trouver le lobby d'attente, veuillez le définir.",
      color=ERROR_COLOR
    ))
    return

  iv_lobby = guild.get_channel(iv_settings.items[IV_LOBBY_ID_KEY].value)

  if iv_lobby is None or not isinstance(iv_lobby, discord.VoiceChannel):
    await message.channel.send(embed=discord.Embed(
      title="Paramètre introuvable",
      description="Impossible de trouver le lobby d'attente, veuillez le définir.",
      color=ERROR_COLOR
    ))
    return

  # exit if no category
  if iv_settings.items[IV_VOICE_CATEGORY_ID_KEY].value == IV_VOICE_CATEGORY_ID_KEY_DEFAULT:
    await message.channel.send(embed=discord.Embed(
      title="Paramètre introuvable",
      description="Impossible de trouver la catégorie réservée à Instant Vocal, veuillez le définir.",
      color=ERROR_COLOR
    ))
    return

  # category must still exist
  iv_category = guild.get_channel(iv_settings.items[IV_VOICE_CATEGORY_ID_KEY].value)
  if iv_category is None or not isinstance(iv_category, discord.CategoryChannel):
    await message.channel.send(embed=discord.Embed(
      title="Instant Vocal: Erreur",
      description="La catégorie pour Instant Vocal n'existe plus. Veuillez la redéfinir.",
      color=ERROR_COLOR
    ))
    return

  if args[0] == 'create':
    # member need to be in lobby    
    if not message.author.voice or message.author.voice.channel != iv_lobby:
      await message.channel.send(embed=discord.Embed(
        title="Instant Vocal: Erreur",
        description="Vous n'êtes pas dans le lobby d'attente",
        color=ERROR_COLOR
      ))
      return
    
    # remove element if empty
    arguments = [el for el in args[1:] if el.strip() != '']

    if len(arguments) == 0:
      return
    
    # last argument optional is the max number
    number = 0
    name = ''

    if len(arguments) == 1:
      name += arguments[0]
    else:
      try:
        max_number = int(arguments[len(arguments) - 1])

        number = max_number
        name = ' '.join(arguments[:len(arguments) - 1])
      except:
        name = ' '.join(arguments)
        pass

    name = name.strip('"')

    if number < 0:
      await message.channel.send(embed=discord.Embed(
        title="Instant Vocal: Erreur",
        description="Le nombre maximum doit être un nombre positif",
        color=ERROR_COLOR
      ))
      return

    tmp_message = await message.channel.send(embed=discord.Embed(
      title=f"Instant Vocal: Création du salon",
      description=f"Création du salon `{ name }` dans la catégorie `{ iv_category.name }`...",
      color=STATUS_COLOR
    ))
    
    iv_guild = await get_instant_vocal_manager(guild=guild, category=iv_category, lobby=iv_lobby)

    iv = await iv_guild.create(creator=message.author, channel_name=name, maxNumber=number)

    await iv.move(message.author)

    iv_settings.items[IV_VOICE_CHANNEL_LIST_KEY].value = iv_guild.to_json()
    iv_settings.save()

  if args[0] == 'invite':
    iv_guild = await get_instant_vocal_manager(guild=guild, category=iv_category, lobby=iv_lobby)

    my_voice = message.author.voice

    # you need to be in vocal
    if my_voice is None:
      await message.channel.send(embed=discord.Embed(
        title="Instant Vocal: Erreur",
        description="Vous n'êtes pas en vocal",
        color=ERROR_COLOR
      ))
      return

    my_voice_channel = my_voice.channel

    # you need to be in a vocal channel
    if my_voice_channel is None:
      await message.channel.send(embed=discord.Embed(
        title="Instant Vocal: Erreur",
        description="Vous n'êtes pas dans un channel vocal",
        color=ERROR_COLOR
      ))
      return
    
    iv = iv_guild.get(my_voice_channel, message.author)

    # author must be in a vocal channel
    if iv is None:
      await message.channel.send(embed=discord.Embed(
        title="Instant Vocal: Erreur",
        description="Vous n'êtes pas dans un Instant Vocal ou ce n'est pas le vôtre",
        color=ERROR_COLOR
      ))
      return

    # add authorization
    for member in message.mentions:
      iv.invite(member)
      try:
        member.move_to(my_voice_channel)
      except:
        pass

async def cmd_instant_vocal_update(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
  # check if not joined
  if before.channel is None:
      return

  # check if multiple persons before
  if len(before.channel.members) > 1:
      return

  guild = before.channel.guild
  guild_id = guild.id

  channel_concerned_id = before.channel.id
      
  # get the iv settings
  iv_settings = get_instant_vocal_settings(guild_id)

  # exit if no lobby
  if iv_settings.items[IV_LOBBY_ID_KEY].value == IV_LOBBY_ID_KEY_DEFAULT:
    return

  iv_lobby = guild.get_channel(iv_settings.items[IV_LOBBY_ID_KEY].value)

  # exit if no category
  if iv_settings.items[IV_VOICE_CATEGORY_ID_KEY].value == IV_VOICE_CATEGORY_ID_KEY_DEFAULT:
    return

  # category must still exist
  iv_category = guild.get_channel(iv_settings.items[IV_VOICE_CATEGORY_ID_KEY].value)

  if iv_lobby is None or not isinstance(iv_lobby, discord.VoiceChannel):
    return

  # get the iv manager
  iv_manager = await get_instant_vocal_manager(guild=guild, category=iv_category, lobby=iv_lobby)
  
  # check if part of the instant channels
  iv = iv_manager.get(before.channel)

  if iv is None:
    return
  
  # so it exists, now get the current channel number
  channel = guild.get_channel(channel_concerned_id)

  # the channel must still exist
  if channel is None:
    return

  # the channel must be empty
  if len(channel.members) > 0:
    return

  # destroy this now
  await iv_manager.destroy(channel=channel)
