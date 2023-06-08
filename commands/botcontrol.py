import discord
import asyncio

from settings import *
from discord.ext.commands import Context, Bot
from utility import convert_dhms


async def cmd_uptime(bot, message, command, args):
    """
    Usage : `{bot_prefix}uptime`
    Renvoie le temps écoulé depuis le lancement du bot
    """
    jours, heures, minutes, secondes = convert_dhms(bot.uptime())
    print("-----------------------------")
    print("Temps écoulé")
    print(f"{jours}:{heures:02d}:{minutes:02d}:{secondes:02d}")
    print("-----------------------------")
    await message.channel.send(
        embed=discord.Embed(
            color=STATUS_COLOR,
            description=f"Temps écoulé depuis démarrage : ``{jours}``j ``{heures}``h ``{minutes}``min ``{secondes}``s",
        )
    )


async def cmd_ping(bot: Context|Bot, message=None, command=None, args=None):
    """
    Usage : `{bot_prefix}ping`
    Renvoie la latence du bot
    """
    latency = bot.bot.latency if isinstance(bot, Context) else bot.latency
    ping = round(latency * 1000)
    message = message if (message is not None) else bot.message

    desc = f"**Ma latence est de ``{ping}``ms** :ping_pong: "

    await message.channel.send(
        embed=discord.Embed(
            color=STATUS_COLOR,
            description=desc,
        )
    )


async def cmd_logout(bot, message, command, args):
    """
    Usage : `{bot_prefix}logout`
    Déconnecte le bot
    """

    ds_role = discord.utils.get(message.guild.roles, name="lvl 30 SNAIL")

    if ds_role not in message.author.roles:
        await message.channel.send(
            embed=discord.Embed(
                title=f"Aide sur {command}",
                description=f"Vous n'avez pas la permission pour faire cette commande",
                color=ERROR_COLOR,
            )
        )
        return

    # disconnects bot from every audio channel
    for index in range(len(bot.voice_clients)):
        vc = bot.voice_clients[index]
        await vc.disconnect()
    jours, heures, minutes, secondes = convert_dhms(bot.uptime())
    alert = await message.channel.send(
        embed=discord.Embed(
            color=STATUS_COLOR,
            description=f"Déconnection.. durée d'execution : ``{jours}j {heures:02d}:{minutes:02d}:{secondes:02d}``",
        )
    )
    await bot.change_presence(
        status=discord.Status.idle, activity=discord.Game(name="Déconnexion..")
    )
    await asyncio.sleep(2)
    await message.delete()
    await alert.delete()
    await bot.logout()
