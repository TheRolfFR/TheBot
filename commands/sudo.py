import discord
import asyncio

from settings import *

COMMAND_SUDO_NAME = "sudo"

async def cmd_sudo(bot: discord.Client, message: discord.Message, command: str, args):
  """
  Command to restart bot
  """
  # message must be authored by the creator
  if message.author.id != CREATOR_ID:
    err = await message.channel.send(embed=discord.Embed(
      title=":no_entry: Access denied :no_entry:",
      color=0xba1930,
      description="You are not allowed to use this command"
    ))
    await asyncio.sleep(7)
    await message.delete()
    await err.delete()
    return

  if len(args) == 0:
    return

  # bla bla access granted thingy
  emb = discord.Embed(
    title=
":white_check_mark: Access granted :white_check_mark:",
    color=0x10ff0d,
    description="Welcome sir"
  )
  result = await message.channel.send(embed=emb)
  
  if(args[0]) == "delete" and len(args) == 2:
    # second thing is the url
    url_split = args[1].split('/')[::-1][:3][::-1]

    # 3 parts guild/channel/id
    try:
      guild = int(url_split[0])
      channel = int(url_split[1])
      msgID = int(url_split[2])
    
      msg = await ((bot.get_guild(guild)).get_channel(channel)).fetch_message(msgID)

      emb.add_field(name="Action", value="Deleting message...", inline=False)
      await result.edit(embed=emb)

      await msg.delete()
    except Exception as e:
      pass
  
  await message.delete()
  await result.delete()