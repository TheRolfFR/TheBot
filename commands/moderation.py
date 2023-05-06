import discord
import asyncio

from settings import *


async def cmd_clear(bot, message, command, args):
    """
    Usage : `{bot_prefix}clear <nombre de messages à supprimer>`
    Supprime les derniers messages
    """

    ds_role = discord.utils.get(message.guild.roles, name="lvl 30 SNAIL")

    is_admin = (
        message.author.guild_permissions.administrator
        or ds_role in message.author.roles
    )

    is_admin = (
        is_admin
        or discord.utils.get(message.guild.roles, name="Admin Service")
        in message.author.roles
    )

    if not is_admin:
        await message.channel.send(
            embed=discord.Embed(
                title=f"Aide sur {command}",
                description=f"Vous n'avez pas la permission pour faire cette commande",
                color=ERROR_COLOR,
            )
        )
        return

    number = 10
    if len(args) > 0:
        if not args[0].isdigit():
            await message.channel.send(embed=bot.doc_embed("clear", ERROR_COLOR))
            return
        number = int(args[0])

    await message.channel.purge(limit=number + 1)
