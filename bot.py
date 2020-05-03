import time
import discord, asyncio
from discord.ext import commands

# yellow color=0xffff00
# green color=0x00ff00

class UTBot (discord.Client):
	def __init__(self, prefix, *args, **kwargs):
		self.launchtime = 0
		self.prefix = prefix
		super().__init__(*args, **kwargs)
	
	def run(self):
		super().run(self.read_token())
	
	def read_token(self):
		with open("token.txt", "r") as f:
			token = f.read().strip()
		return token
	
	def uptime(self):
		return time.time() - self.launchtime
		
def convert_dhms(duration):
	duration = int(duration)
	return (duration // 86400, (duration // 3600) % 24, (duration // 60) % 60, duration % 60)

def convert_hms(duration):
	duration = int(duration)
	return (duration // 3600, (duration // 60) % 60, duration % 60)
		
bot = UTBot("=")

docs = {
	"uptime": f"Usage : `{bot.prefix}uptime`\nRenvoie le temps écoulé depuis le lancement du bot",
	"clear": f"Usage : `{bot.prefix}clear <nombre de messages à supprimer>`\nSupprime les derniers messages",
	"logout": f"Usage : `{bot.prefix}logout`\nDéconnecte le bot",
	"ping": f"Usage : `{bot.prefix}ping`\nRenvoie la latence du bot",
}

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
	await asyncio.sleep(4)
	bot.launchtime = time.time()
	await bot.change_presence(status=discord.Status.online, activity=discord.Game(name="Opérationnel !"))

# Liste des commandes
@bot.event
async def on_message(message):
	if message.author.id == bot.user.id: return  # Évite que le bot traite ses propres messages, en général optimisation mineure, mais ça peut éviter des soucis dans certains cas
	
	if message.content.startswith(bot.prefix):  # Filtre les commandes d’entrée
		jours, heures, minutes, secondes = convert_dhms(bot.uptime())
		
		# Découpage de la commande `<prefixe><commande> <arg1> <arg2> …`
		commandtokens = message.content.lstrip(bot.prefix).split(" ")
		command = commandtokens[0]
		args = commandtokens[1:]
		
		if command == "uptime":
			jours, heures, minutes, secondes = convert_dhms(bot.uptime())
			print("-----------------------------")
			print("Temps écoulé")
			print(f"{jours}:{heures:02d}:{minutes:02d}:{secondes:02d}")
			print("-----------------------------")
			await message.channel.send(f"Temps écoulé depuis démarrage : ``{jours}``j ``{heures}``h ``{minutes}``min ``{secondes}``s")


		elif command == "clear":
			if len(args) != 1:
				await message.channel.send(docs["clear"])
				return
			if not args[0].isdigit():
				await message.channel.send(docs["clear"])
				return
				
			number = int(args[0])

			print("-----------------------------")
			print("Clear text")
			print(f"{jours:02d}:{heures:02d}:{minutes:02d}:{secondes:02d}")
			print("-----------------------------")

			await message.channel.purge(limit=number +1)
			await message.channel.send(embed=discord.Embed(color=0x00ff00, description=f":x: **``{number}`` messages supprimé(s)** :x:"))
			await asyncio.sleep(6)
			await message.channel.purge(limit=1)

		elif command == "ping":
			print("-----------------------------")
			print("Ping")
			print(f"{jours}:{heures:02d}:{minutes:02d}:{secondes:02d}")
			print("-----------------------------")
			ping = round(bot.latency * 1000)
			await message.channel.send(embed=discord.Embed(color=0x00ff00, description=f"**Ma latence est de ``{ping}``ms** :ping_pong: "))
		
		elif command == "logout":
			print("-----------------------------")
			print("Logout")
			print("-----------------------------")
			heures, minutes, secondes = convert_hms(bot.uptime())
			await message.channel.send(embed=discord.Embed(color=0xffff00, description=f"Déconnection.. durée d'execution : ``{jours}j {heures:02d}:{minutes:02d}:{secondes:02d}``"))
			await bot.change_presence(status=discord.Status.idle, activity=discord.Game(name="Déconnexion.."))
			await asyncio.sleep(2)
			await message.channel.purge(limit=2)
			await bot.logout()
		
		elif command == "help":
			if len(args) != 1:
				await message.channel.send(docs["help"])
			elif args[0] not in docs.keys():
				await message.channel.send(docs["help"])
			else:
				await message.channel.send(docs[args[0]])

bot.run()