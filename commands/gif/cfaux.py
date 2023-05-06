import discord
import asyncio

from .gif_maker import cmd_gifmaker

CVRAI_TITRE = "C'EST FAUX"


async def cmd_cfaux(bot: discord.Client, message: discord.Message, command: str, args):
    """Commande meme c'est faux: `{bot_prefix}cfaux <message d'explication (optionnel)>` + pièce jointe avec image: Affiche l'image dans un cadre avec le message d'explication
    L'auteur peut réagir avec 🗑 pour supprimer le gif jusqu'à 30s après la publication du GIF
    """
    await cmd_gifmaker(bot, message, command, args, CVRAI_TITRE)
