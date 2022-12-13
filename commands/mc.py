import discord
from mojang import API as MojangAPI

import requests, json
from settings import *

from datetime import datetime
import random
import os

async def cmd_mc(bot: discord.Client, message: discord.Message, command: str, args):
  """
  Commande Minecraft, server ping, couleurs mc, skins, etc...
  `{bot_prefix}mc colors` : Affiche les codes couleurs Minecraft
  `{bot_prefix}mc get <texte>` : Affiche un succès minecraft
  `{bot_prefix}mc lookup <uuid|pseudo>` : Affiche l'historique des noms d'un joueur
  `{bot_prefix}mc ping <ip>` : Ping un serveur et retourne son état
  `{bot_prefix}mc skin <uuid|pseudo>` : Affiche le skin du joueur
  `{bot_prefix}mc status` : Affiche l'historique des noms pour d'un uuid ou un pseudo minecraft
  `{bot_prefix}mc username <uuid>` : Affiche le pseudo pour d'un uuid minecraft
  `{bot_prefix}mc uuid <pseudo>` : Affiche l'uuid d'un pseudo minecraft
  """
  if isinstance(args, str): args = [args]

  if len(args) < 1: return

  subcommand = args[0]
  if subcommand == "colors":
    await message.channel.send(file=discord.File(os.path.join(os.getcwd(), 'resources', 'mc_colors.jpg')))
    return
  
  if subcommand == "get":
    text = " ".join(args[1:]).strip()
    text = text.replace('+', '\+')
    text = text.replace(" ", "+")
    image_url = 'https://minecraftskinstealer.com/achievement/' + str(random.randint(0, 39)) + '/Achievement+Get!/' + text
    await message.channel.send(image_url)
    return

  if subcommand == "uuid":
    recherche = "".join(args[1:])
    uuid = MojangAPI.get_uuid(recherche)
    if not uuid:
      await message.reply(
        embed=discord.Embed(
          title="UUID introuvable",
          color=ERROR_COLOR,
          description= f"Pas de résultats pour \"{ recherche }\""
        ),
        mention_author=False
      )
      return
    else:
      await message.reply(
        embed=discord.Embed(
          title="UUID pour " + recherche,
          color=STATUS_COLOR,
          description= f"{ uuid }"
        ),
        mention_author=False
      )
      return
  
  if subcommand == "username":
    recherche = "".join(args[1:])
    pseudo = MojangAPI.get_username(recherche)
    if not pseudo:
      await message.reply(
        embed=discord.Embed(
          title="Pseudo introuvable",
          color=ERROR_COLOR,
          description= f"Pas de résultats pour \"{ recherche }\""
        ),
        mention_author=False
      )
      return
    else:
      await message.reply(
        embed=discord.Embed(
          title="Pseudo pour " + recherche,
          color=STATUS_COLOR,
          description= f"{ pseudo }"
        ),
        mention_author=False
      )
      return

  if subcommand == "lookup":
    recherche = "".join(args[1:]).strip()
    uuid = MojangAPI.get_uuid(recherche)
    if not uuid:
      uuid = recherche
  
    try:
      name_history = MojangAPI.get_name_history(uuid)
    except:
      pass

    if (not name_history) or len(name_history) == 0:
        await message.reply(
          embed=discord.Embed(
            title="Aucun résultat",
            color=ERROR_COLOR,
            description= f"Pas de résultats pour \"{ recherche }\""
          ),
          mention_author=False
        )
        return
    
    embed = discord.Embed(
      title="Historique des noms pour " + recherche,
      color=STATUS_COLOR
    )
    for data in name_history:
      if data['changed_to_at'] == 0:
        embed.add_field(name="Premier", value='``' + data['name'] + '``', inline=True)
      else:
        int_time = data['changed_to_at'] / 1000
        time = datetime.fromtimestamp(int_time)
        embed.add_field(name=str(time.strftime('%d/%m/%Y')), value='``' + data['name'] + '``', inline=True)
    
    await message.reply(
      embed=embed,
      mention_author=False
    )
    return

  if subcommand == "status":
    try:
      data = MojangAPI.get_api_status()
    except:
      await message.reply(
        embed=discord.Embed(
          title="Service down",
          color=ERROR_COLOR,
          description= f"Le service de status de Mojang est down.\nMerci de réessayer plus tard."
        ),
        mention_author=False
      )
      return

    embed = discord.Embed(
      title="Status des service minecraft",
      color=STATUS_COLOR
    )
    for server, status in data.items():
      if status == "red":
        embed.add_field(name=server, value= ':red_circle:', inline=False)
      else:
        embed.add_field(name=server, value= ':green_circle:', inline=False)
    
    await message.reply(
      embed=embed,
      mention_author=False
    )
    return

  if subcommand == "skin":
    recherche = "".join(args[1:]).strip()
    uuid = MojangAPI.get_uuid(recherche)
    if not uuid:
      uuid = recherche

    final_url = 'https://mc-heads.net/body/' + uuid
    await message.reply(final_url, mention_author=False)
    return

  if subcommand == "ping":
    recherche = "".join(args[1:]).strip()

    url = ' https://api.mcsrvstat.us/2/' + recherche
    response = requests.get(url)
    data = json.loads(response.text)

    embed = discord.Embed(
      title="MSS: " + recherche,
      color=STATUS_COLOR
    )

    online = data['online']
    embed.add_field(name='En ligne', value='Oui' if online else 'Non', inline=False)

    if online:
      embed.add_field(name='IP', value=str(data['ip']) + ':' + str(data['port']), inline=False)
      embed.add_field(name='motd', value="\n".join(data['motd']['clean']))
      embed.add_field(name='Joueurs', value=str(data['players']['online']) + '/' + str(data['players']['max']), inline=False)
      if data['players']['online'] > 0:
        embed.add_field(name='Liste des joueurs', value=', '.join(data['players']['list']), inline=False)
      embed.add_field(name='Version', value=data['version'], inline=False)

      if data['mods'] is not None:
        embed.add_field(name="Mods", value='Oui (' + str(len(data['mods']['names'])) + ')', inline=False)

    await message.reply(embed=embed, mention_author=False)
    return


