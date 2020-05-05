import discord
import asyncio

from data import *
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
	await message.channel.send(embed=discord.Embed(color=status_color, description=f"Temps écoulé depuis démarrage : ``{jours}``j ``{heures}``h ``{minutes}``min ``{secondes}``s"))


async def cmd_ping(bot, message, command, args):
	"""
	Usage : `{bot_prefix}ping`
	Renvoie la latence du bot
	"""
	ping = round(bot.latency * 1000)
	await message.channel.send(embed=discord.Embed(color=status_color, description=f"**Ma latence est de ``{ping}``ms** :ping_pong: "))
	
async def cmd_logout(bot, message, command, args):
	"""
	Usage : `{bot_prefix}logout`
	Déconnecte le bot
	"""
	print("-----------------------------")
	print("Logout")
	print("-----------------------------")
	jours, heures, minutes, secondes = convert_dhms(bot.uptime())
	alert = await message.channel.send(embed=discord.Embed(color=status_color, description=f"Déconnection.. durée d'execution : ``{jours}j {heures:02d}:{minutes:02d}:{secondes:02d}``"))
	await bot.change_presence(status=discord.Status.idle, activity=discord.Game(name="Déconnexion.."))
	await asyncio.sleep(2)
	await message.delete()
	await alert.delete()
	await bot.logout()