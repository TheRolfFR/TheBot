import discord
import asyncio

from .gif_maker import cmd_gifmaker

CVRAI_TITRE = "C'EST VRAI"

async def cmd_cvrai(bot: discord.Client, message: discord.Message, command: str, args):
  """Commande meme c'est vrai: `{bot_prefix}cvrai <message d'explication (optionnel)>` + pièce jointe avec image: Affiche l'image dans un cadre avec le message d'explication"""
  await cmd_gifmaker(bot, message, command, args, CVRAI_TITRE)