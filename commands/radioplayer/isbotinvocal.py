
# returns whether the bot is in the channel with its member else None
async def isBotInChannel(bot, voice_channel):
  channelMembers = voice_channel.members

  meMember = None
  index = 0
  while index < len(channelMembers) and meMember == None:
    if channelMembers[index].id == bot.user.id:
      meMember = channelMembers[index]
    index = index + 1

  return meMember