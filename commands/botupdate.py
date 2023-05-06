import discord
from discord.ext import commands
import asyncio
import git
import sys
import os

from settings import *

COMMAND_UPDATE_NAME = "updatebot"

REBOOT_MESSAGE_ID_PATH = os.path.join(os.getcwd(), "data", "rebootmessageid.txt")


async def cmd_update_bot(
    bot: discord.Client, message: discord.Message, command: str, args
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

    # bla bla access granted thingy
    emb = discord.Embed(
        title=":white_check_mark: Access granted :white_check_mark:",
        color=0x10FF0D,
        description="Welcome sir",
    )
    result = await message.channel.send(embed=emb)

    await message.delete()
    await bot.change_presence(status=discord.Status.idle)

    # write message id
    try:
        os.makedirs(os.path.dirname(REBOOT_MESSAGE_ID_PATH))
    except:
        pass

    with open(REBOOT_MESSAGE_ID_PATH, "w") as f:
        f.writelines(
            [
                str(result.channel.guild.id) + "\n",
                str(result.channel.id) + "\n",
                str(result.id) + "\n",
            ]
        )
        f.flush()

    emb.add_field(name="Git", value="Pulling changes...", inline=False)
    await result.edit(embed=emb)

    g = git.cmd.Git(os.getcwd())
    g.pull()

    emb.add_field(name="Restart", value="Restarting bot...", inline=False)
    await result.edit(embed=emb)

    python = sys.executable
    os.execl(python, python, *sys.argv)


async def reboot_successful(bot: discord.Client):
    try:
        with open(REBOOT_MESSAGE_ID_PATH, "r") as f:
            value = f.read()

        arr = value.split("\n")
        guild = int(arr[0])
        channel = int(arr[1])
        msgID = int(arr[2])

        msg = await bot.get_guild(guild).get_channel(channel).fetch_message(msgID)

        emb = msg.embeds[0]

        with open(REBOOT_MESSAGE_ID_PATH, "w") as f:
            f.write("")
            f.flush()

        for i in range(5, 0, -1):
            if i != 5:
                emb.remove_field(len(emb.fields) - 1)
            emb.add_field(
                name="Reboot successful",
                value="This message will self-destruct in "
                + str(i)
                + " second"
                + ("s" if i > 1 else ""),
                inline=False,
            )
            await msg.edit(embed=emb)
            await asyncio.sleep(1)

        await msg.delete()
    except Exception as e:
        pass
