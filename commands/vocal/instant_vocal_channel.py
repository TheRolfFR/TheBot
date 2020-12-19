import discord
import asyncio

class InstantVocalChannel:
  """Instant vocal channel handler"""
  __channel: discord.VoiceChannel
  __max_number: int
  __creator_id: int
  __authorized_members_id: list

  def __init__(self):
    self.__channel = None
    
  async def init(self, guild: discord.Guild, category: any, creator_id: int, maxNumber: int, channel_name = '', channel_id = -1):
    if not isinstance(channel_name, str) or not isinstance(channel_id, int):
      raise TypeError('Incorrect parameter types for constructor')

    if category is not None and not isinstance(category, discord.CategoryChannel):
      raise TypeError(f'Category type incorrect, expected { discord.CategoryChannel, }, got { type(category) }')

    if channel_name == '' and channel_id < 0:
      raise ValueError('Expecting channel name or id')

    if channel_name != '' and channel_id > -1:
      raise ValueError('Expecting channel name or id')

    # create channel
    if channel_name != '':
      iv_channel = await guild.create_voice_channel(channel_name,
        category=category,
        reason="TheBot created an IV",
        user_limit=maxNumber,
        overwrites = {
          guild.default_role: discord.PermissionOverwrite(connect=False),
        }
      )
      self.__channel = iv_channel

    # find channel
    elif channel_id > -1:
      iv_channel = guild.get_channel(channel_id)
      if iv_channel is None:
        raise ValueError("Can't find channel")
      self.__channel = iv_channel
    
    self.__max_number = maxNumber

    self.__creator_id = creator_id
    self.__authorized_members_id = [creator_id]

  async def move(self, member: discord.Member):
    await member.move_to(self.__channel)

  def exist(self):
    return self.__channel != None

  def invite(self, member: discord.Member):
    self.__authorized_members_id.append(member.id)

  def uninvite(self, member: discord.Member):
    self.__authorized_members_id.remove(member.id)

  def to_json(self):
    if not self.exist():
      return None
    
    return dict(
      creator = self.__creator_id,
      channel_id = self.__channel.id,
      max_number = self.__max_number,
      authorized_members = self.__authorized_members_id 
    )

  @property
  def channel(self):
    return self.__channel

  @property
  def creator_id(self):
    return self.__creator_id

class InstantVocalManager:
  """Class manging instant vocal sessions"""
  __guild: discord.Client
  __lobby: discord.VoiceChannel
  __category: discord.CategoryChannel
  __list: list

  def __init__(self, guild: discord.Guild, category: discord.CategoryChannel, lobby: discord.VoiceChannel):
    self.__guild = guild
    self.__lobby = lobby
    self.__category = category
    self.__list = []

  async def init(self, json_list: list):
    for el in json_list:
      try:
        iv_channel = InstantVocalChannel()
        await iv_channel.init(guild=self.__guild, creator_id=el['creator'], category=self.__category, maxNumber=el['max_number'], channel_id=el['channel_id'])
        self.__list.append(iv_channel)
      except BaseException as e:
        print(str(e))

  async def create(self, creator: discord.Member, channel_name: str, maxNumber: int):
    iv_channel = InstantVocalChannel()
    await iv_channel.init(guild=self.__guild, creator_id=creator.id, category=self.__category, maxNumber=maxNumber, channel_name=channel_name)
    self.__list.append(iv_channel)

    return iv_channel

  def get(self, channel: discord.VoiceChannel, author=None):
    i = 0
    while i < len(self.__list):
      if self.__list[i].channel == channel and (author is None or self.__list[i].creator_id == author.id):
        return self.__list[i]

      i += 1

    return None

  async def destroy(self, channel: discord.VoiceChannel):
    el = self.get(channel)

    if el is None:
      return

    self.__list.remove(el)

    await el.channel.delete(reason="TheBot deleted IV because empty")

  def to_json(self):
    result = []

    for el in self.__list:
      result.append(el.to_json())

    return result

  def guild_id(self):
    return self.__guild.id