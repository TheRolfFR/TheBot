import discord

async def voiceClient(bot: discord.Client, sessionID: str):
  result = None

  vcList = bot.voice_clients

  index = 0
  while index < len(vcList) and result is None:
    if vcList[index].session_id == sessionID:
      result = vcList[index]
    index = index + 1

  return result