import sys
import json
from os import makedirs
from os.path import abspath, join, dirname

def get_settings_folder_path(guild_id: int):
  return abspath(join(dirname(__file__), '..', '..', 'data', str(guild_id)))

def get_settings_path(guild_id: int):
  return join(get_settings_folder_path(guild_id), 'settings.json')

def get_setting(guild_id: int, field: str):
  set_path = get_settings_path(guild_id)

  settings = {}
  try:
    f = open(set_path, 'r')
    raw = f.read()
    f.close()

    settings_json = json.loads(raw)
    settings = settings_json
  except Exception as e:
    # print("Error while reading current settings")
    # print(e)
    return None

  # get value
  if field in settings:
    return settings[field]

  return None

def set_setting(guild_id: int, field: str, value: any):
  set_path = get_settings_path(guild_id)

  settings = {}
  try:
    f = open(set_path, 'r')
    raw = f.read()
    f.close()

    settings_json = json.loads(raw)
    settings = settings_json
  except Exception as e:
    # print("Error while reading settings file to write them")
    # print(e)
    pass

  # apply value
  settings[field] = value

  try:
    makedirs(get_settings_folder_path(guild_id), exist_ok = True)

    f = open(set_path, 'w')
    f.write(json.dumps(settings))
    f.close()
  except Exception as e:
    print("Error while writing settings file")
    print(e)
    return

class GuildSettingGroup:
  """Guild setting group with key and items"""
  __guild_id: int
  __field: str
  items: list
  raw: any

  def __init__(self, guild_id: int, field: str):
    self.__field = field
    self.__guild_id = guild_id

    self.items = {}

    self.raw = get_setting(guild_id, field)

    if self.raw is None:
      self.raw = {}

  @property
  def field(self):
    """Key of the setting"""
    return self.__field

  @field.setter
  def field(self, val):
    return

  @property
  def guild_id(self):
    """Guild ID of the setting"""
    return self.__guild_id

  @guild_id.setter
  def guild_id(self, val):
    return

  def create_item(self, key: str, item_type: type, default:any=None):
    """Get or create an item of the group"""
    if key not in self.items:
      self.items[key] = GuildSettingItem(self, key, item_type, default)
    
    return self.items[key]
  
  def save(self):
    set_setting(self.__guild_id, self.__field, self.raw)

  def __eq__(self, o):
    """== operator overload"""
    if isinstance(o, int):
      return o == self.__guild_id

    return False

class GuildSettingItem:
  """Guild setting item interface with key, type and optional default value"""
  __group: GuildSettingGroup

  __key: str
  __type: type
  __default: any

  def __init__(self, group: GuildSettingGroup, key: str, item_type: type, default:any=None):
    self.__group = group

    self.__key = key
    self.__type = item_type
    self.__default = default

    if not key in self.__group.raw:
      self.__group.raw[key] = self.__default

  @property
  def key(self):
    """Key of the setting"""
    return self.__key

  @key.setter
  def key(self, val):
    return
  
  @property
  def value(self):
    """Value of the setting"""
    if self.__key in self.__group.raw and isinstance(self.__group.raw[self.__key], self.__type):
      return self.__group.raw[self.__key]
    
    return self.__default

  @value.setter
  def value(self, value: any):
    if not isinstance(value, self.__type):
      raise TypeError(f'Incorrect type, expected { self.__type }, got { type(value) }')

    self.__group.raw[self.__key] = value
