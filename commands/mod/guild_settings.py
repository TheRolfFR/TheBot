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