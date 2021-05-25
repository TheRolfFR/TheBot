import discord

from settings import *

import os
import sys
import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 

from libs.larousse_api.larousse import Larousse

async def cmd_larousse(bot: discord.Client, message: discord.Message, command: str, args):
  """
  Commande Larousse, recherche des définitions, des synonymes et des citations
  `{bot_prefix}larousse <recherche>` : affiche les définitionq pour <recherche>
  `{bot_prefix}larousse definition <recherche>` : affiche les définitionq pour <recherche>
  `{bot_prefix}larousse synonymes <recherche>` : affiche les synonymes pour <recherche>
  `{bot_prefix}larousse citations <recherche>` : affiche les synonymes pour <recherche>
  """

  guild = message.guild
  if guild is None:
        return

  # elimine "{bot_prefix}larousse" command
  if isinstance(args, list) and len(args) == 0:
    return

  infoType = ""
  search = ""
 
  if isinstance(args, str): # cas "{bot_prefix}larousse <search>"
    infoType = "definition"
    search = args
  elif isinstance(args, list) and len(args) == 1:
    infoType = "definition"
    search = args[0]
  else: # cas "{bot_prefix}larousse <infoType> <search>"
    infoType = args[0]
    if not (args[0] in ["definition", "synonymes", "citations"]):
      infoType = "definition"
      search = " ".join(args)
    else:
      infoType = args[0]
      search = " ".join(args[1:])

  print(infoType, search)

  if not (infoType in ["definition", "synonymes", "citations"]):
    return

  # demarrage de la recherche
  await message.add_reaction("🔍")

  #titre
  content = "**" + infoType[0].upper() + infoType[1:] + " pour \"" + search + "\"**"
  l = Larousse(search)

  #resultat de la recherche
  res = (None, None)

  #contenu
  if infoType == "definition":
    res = l.get_definitions()
  elif infoType == "synonymes":
    res = l.get_synonymes()
  else:
    res = l.get_citations()

  #fin recherche
  await message.clear_reaction("🔍")

  if res[0] is not None:
    phrases = res[0]
    for phrase in phrases:
      mots = phrase.split(" ")

      # detecter domaine comme Medecine et rajouter " - "
      cap_temp_list = [c for c in mots[0] if c.isupper()]
      if len(cap_temp_list) > 1:
        capital_pos = mots[0].index(cap_temp_list[1])
        if(capital_pos > 2):
          mots[0] = str(mots[0][:capital_pos]) + ' - ' + str(mots[0][capital_pos:])

      phrase = " ".join(mots) # on recree la phrase

      if(len(content + "\n• " + phrase) > 2000):
        await message.reply(content)
        content = ""
      content += "\n• " + phrase #autres tirets

    await message.reply(content)
  else:
    await message.reply(
      embed=discord.Embed(
        title="Larousse : recherche introuvable",
        color=ERROR_COLOR,
        description= f"Pas de résultats pour \"{ search }\""
      )
    )