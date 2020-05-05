import discord
import asyncio
from data import *

async def cmd_clear(bot, message, command, args):
	"""
	Usage : `{bot_prefix}clear <nombre de messages à supprimer>`
	Supprime les derniers messages
	"""
	if len(args) != 1:
		await message.channel.send(embed=bot.doc_embed("clear", error_color))
		return
	if not args[0].isdigit():
		await message.channel.send(embed=bot.doc_embed("clear", error_color))
		return
		
	number = int(args[0])

	await message.channel.purge(limit=number +1)
	alert = await message.channel.send(embed=discord.Embed(color=confirm_color, description=f":x: **``{number}`` messages supprimé(s)** :x:"))
	await asyncio.sleep(6)
	await alert.delete()