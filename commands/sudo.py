import discord
import asyncio
import os

from settings import *

COMMAND_SUDO_NAME = "sudo"


async def cmd_sudo(
    bot: discord.Client, message: discord.Message, command: str, args, voicePlayers
):
    """
    Command to restart bot
    """
    # message must be authored by the creator
    if message.author.id != CREATOR_ID:
        err = await message.channel.send(
            embed=discord.Embed(
                title=":no_entry: Access denied :no_entry:",
                color=0xBA1930,
                description="You are not allowed to use this command",
            )
        )
        await asyncio.sleep(7)
        await message.delete()
        await err.delete()
        return

    if len(args) == 0:
        return

    if args[0] == "say":
        await message.delete()
        await message.channel.send(" ".join(args[1:-1]))
        return

    # bla bla access granted thingy
    emb = discord.Embed(
        title=":white_check_mark: Access granted :white_check_mark:",
        color=0x10FF0D,
        description="Welcome sir",
    )
    result = await message.channel.send(embed=emb)

    subcommand = args[0]

    if subcommand == "delete" and len(args) >= 2:
        # second thing is the url
        url_split = args[1].split("/")[::-1][:3][::-1]

        # 3 parts guild/channel/id
        try:
            guild = int(url_split[0])
            channel = int(url_split[1])
            msgID = int(url_split[2])

            msg = await bot.get_guild(guild).get_channel(channel).fetch_message(msgID)

            emb.add_field(name="Action", value="Deleting message...", inline=False)
            await result.edit(embed=emb)
            await asyncio.sleep(2)
            await msg.delete()
        except Exception as e:
            pass

    if subcommand == "nggyu" and len(args) >= 2:
        user_targeted = (
            message.mentions[0] if len(message.mentions) > 0 else message.author
        )

        from commands.player.radio import cmd_radio
        cmd_radio(bot, message, ["play", "nggyu"], user_targeted, voicePlayers)

        emb.add_field(name="Action", value="Lancement du troll...", inline=False)
        await result.edit(embed=emb)
        await asyncio.sleep(2)

    await message.delete()
    await result.delete()
