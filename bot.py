import discord, asyncio
from discord.ext import commands

# yellow color=0xffff00
# green color=0x00ff00

def read_token():
	with open("token.txt", "r") as f:
		lines = f.readlines()
		return lines[0].strip()

token = read_token()

prefix = '='
bot = commands.Bot(command_prefix=prefix)

secondes = -1
minutes = 0
heures = 0
jours = 0

@bot.event
async def on_ready():
	await bot.change_presence(status=discord.Status.idle, activity=discord.Game(name="Démarrage.."))
	print('-----------------------------')
	print('Demarrage..')
	print('version discord.py :',discord.__version__)
	print("Name: {0.user}".format(bot))
	print("ID: {}".format(bot.user.id))
	print(f"Serving: {len(bot.guilds)} guilds.")
	print('-----------------------------')
	await asyncio.sleep(4)
	await bot.change_presence(status=discord.Status.online, activity=discord.Game(name="Opérationnel !"))

async def my_background_task():
	global secondes,minutes,heures,jours
	await bot.wait_until_ready()
	print('-----------------------------')
	print("Demarrage de l'horloge")
	print('-----------------------------')
	while not bot.is_closed():
		secondes += 1
		if secondes >= 59:
			minutes += 1
			secondes = 0
			if minutes >= 59:
				heures += 1
				minutes = 0
				if heures == 24:
					jours += 1
					heures = 0
		await asyncio.sleep(1)

# Liste des commandes
@bot.event
async def on_message(message):
	global secondes,minutes,heures

	if message.content.startswith(prefix + 'time'):
		print('-----------------------------')
		print("Temps écoulé")
		print(f'{jours}:{heures}:{minutes}:{secondes}')
		print('-----------------------------')
		await message.channel.send(f'Temps écoulé depuis démarrage : ``{jours}``j ``{heures}``h ``{minutes}``min ``{secondes}``s')


	if message.content.startswith(prefix + 'clear '):
		str_number = message.content[len(prefix)+6:]
		try:
			number = int(str_number)

			if number <= 0:
				await message.channel.send(embed=discord.Embed(color=0xffff00, description='Entrez un entier supérieur à 0'))
				await asyncio.sleep(6)
				await message.channel.purge(limit=2)

			else:
				print('-----------------------------')
				print("Clear texte")
				print(f'{jours}:{heures}:{minutes}:{secondes}')
				print('-----------------------------')

				await message.channel.purge(limit=number +1)
				await message.channel.send(embed=discord.Embed(color=0x00ff00, description=f':x: **``\n{number}`` messages suprimé(s)** :x:'))
				await asyncio.sleep(6)
				await message.channel.purge(limit=1)

		except:
			await message.channel.send(embed=discord.Embed(color=0xffff00, description='Entrez un entier'))
			await asyncio.sleep(6)
			await message.channel.purge(limit=2)

	if message.content.startswith(prefix + 'logout'):
		print('-----------------------------')
		print('logout')
		print('-----------------------------')
		await message.channel.send(embed=discord.Embed(color=0xffff00, description=f"Déconnection.. durée d'execution : ``{heures}:{minutes}:{secondes}``"))
		await bot.change_presence(status=discord.Status.idle, activity=discord.Game(name="Déconnection.."))
		await asyncio.sleep(2)
		await message.channel.purge(limit=2)
		await bot.logout()

	if message.content.startswith(prefix + 'ping'):
		print('-----------------------------')
		print("Ping")
		print(f'{jours}:{heures}:{minutes}:{secondes}')
		print('-----------------------------')
		ping_ = bot.latency
		ping = round(ping_ * 1000)
		await message.channel.send(embed=discord.Embed(color=0x00ff00, description=f"**Ma latence est de ``{ping}``ms** :ping_pong: "))

bot.loop.create_task(my_background_task())
bot.run(token)