import time
import asyncio
import os

import discord
import asyncio

import googletrans

import keep_alive

from settings import *
from commands import *
from commands.mod import cmd_hardlog_update
from commands.botupdate import *

class UTBot (discord.Client):
	def __init__(self, prefix, *args, **kwargs):
		self.launchtime = 0
		self.prefix = prefix
		super().__init__(*args, **kwargs)
	
	def run(self):
		super().run(self.read_token())

		print("-----------------------------")
		print("Logout")
		print("-----------------------------")

		# when stoppped

		# stop radio
		for player in laRadio.players:
			asyncio.run(player.stop())

		# stop keep alive
		keep_alive.stop()
	
	def read_token(self):
		token = os.environ.get("DISCORD_TOKEN", "")

		if token == "":
			f = open("token.txt")
			token = f.read()
			f.close()

		return token
	
	def uptime(self):
		return time.time() - self.launchtime
	
	def doc_embed(self, command, color):
		if command == "help":
			text = cmd_help.__doc__
		elif command == "rageux":
			text = cmd_rageux.__doc__
		else:
			text = BOT_COMMANDS[command].__doc__
		return discord.Embed(title=f"Aide sur {command}", description=text.format(bot_prefix=self.prefix), color=color)

my_intents = discord.Intents.default()
my_intents.guilds = True
my_intents.members = True
my_intents.voice_states = True
bot = UTBot(PREFIX, intents=my_intents)

@bot.event
async def on_ready():
	await bot.change_presence(status=discord.Status.idle, activity=discord.Game(name="Démarrage.."))
	print("-----------------------------")
	print("Demarrage..")
	print(f"Version discord.py : {discord.__version__}")
	print(f"Name: {bot.user}")
	print(f"ID: {bot.user.id}")
	print(f"Serving: {len(bot.guilds)} guilds.")
	print("-----------------------------")

	await bot.change_presence(status=discord.Status.online, activity=discord.Game(name=f'{ bot.prefix }help'))
	
	# reboot successful message end
	await reboot_successful(bot)
	


async def cmd_help(bot, message, command, args):
	"""
	Usage : `{bot_prefix}help <commande>`
	Donne de l’aide sur une commande
	"""
	command_map = (BOT_COMMANDS | BOT_SPECIAL_COMMANDS) if SPECIAL_SERVERS.index(message.guild.id) != -1 else BOT_COMMANDS

	if len(args) == 0:
		commandlist = list(command_map.keys())
		commandlist.sort()
		await message.channel.send(embed=discord.Embed(color=HELP_COLOR, title="Liste des commandes", description="\n".join(list(commandlist)) + f"\n\nUtilisez `{bot.prefix}help <commande>` pour plus d’informations sur une commande"))
	elif len(args) > 1:
		await message.channel.send(embed=bot.doc_embed("help", ERROR_COLOR))
	else:
		commandlist = list(command_map.keys())
		
		if args[0] in commandlist or args[0] == "help":
			await message.channel.send(embed=bot.doc_embed(args[0], HELP_COLOR))
		else:
			await message.channel.send(embed=discord.Embed(color=ERROR_COLOR, description=f"La commande {args[0]} est inconnue"))
			await message.channel.send(embed=discord.Embed(color=ERROR_COLOR, title="Liste des commandes", description="\n".join(list(BOT_COMMANDS.keys()))))


@bot.event
async def on_message(message):
	if message.author.id == bot.user.id: return  # Évite que le bot traite ses propres messages, en général optimisation mineure, mais ça peut éviter des soucis dans certains cas
	
	if message.content.startswith(bot.prefix):  # Filtre les commandes d’entrée
		# Découpage de la commande `<prefixe><commande> <arg1> <arg2> …`
		commandtokens = message.content[len(bot.prefix):].split(" ")
		command = commandtokens[0]
		args = commandtokens[1:]

		command_map = (BOT_COMMANDS | BOT_SPECIAL_COMMANDS) if SPECIAL_SERVERS.index(message.guild.id) != -1 else BOT_COMMANDS

		if "\n" in command:
			firstindex = command.find("\n")

			#rebuild commands
			cmd = command[:firstindex]

			if isinstance(args, str):
				args = [args]

			args = [command[(firstindex+1):]] + args
			
			# replace new command
			command = cmd

		if command == "help":
			await cmd_help(bot, message, command, args)
		elif command == COMMAND_UPDATE_NAME:
			await cmd_update_bot(bot, message, command, args)
		elif command in BOT_COMMANDS.keys():
			await BOT_COMMANDS[command](bot, message, command, args)
			
@bot.event
async def on_message_edit(before, after):
	await on_message(after)
	await cmd_hardlog_update(
		bot=bot,
		message_original=before,
		message_edite=after,
		edit=True,
		delete=False
	)

@bot.event
async def on_voice_state_update(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
	await laRadio.update(member, before, after)

@bot.event
async def on_message_delete(message: discord.Message):
	await cmd_hardlog_update(
		bot=bot,
		message_original=message,
		message_edite=None,
		edit=False,
		delete=True
	)

# start the server to stay alive
keep_alive.start()

bot.run()

# permission integer: 301067378
# permission integer 8 is administrator
# invite link be like https://discord.com/oauth2/authorize?client_id=<client_id>&permissions=<permission_number>&scope=bot
# invite link be like https://discord.com/oauth2/authorize?client_id=<client_id>&permissions=301067378&scope=bot
