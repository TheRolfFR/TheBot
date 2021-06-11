import discord
import asyncio

# path things
import os

from .gifcreator import GIFCreator
from .gifcreator.text_property import TextProperty

GHIS_CAPTION = "Et que vive"
GHIS_CAPTION_PADDING = 6
GHIS_CAPTION_BACKGROUND = (0, 0, 0, int(20))
GHIS_FONT_SIZE = 52
GHIS_BOTTOM_MARGIN = 20

pathGIFGhis = os.path.join(os.getcwd(), "resources", "ghis.gif")
ghisGIF = GIFCreator.loadImageFromPath(pathGIFGhis)

async def cmd_ghis(bot: discord.Client, message: discord.Message, command: str, args):
  """
  Commande des meilleurs vives du ghis
  ``{bot_prefix}ghis l'UTBiscord`` Affiche un gif du ghis
  """
  ghis_message = " ".join(args)
  
  ghis_creator = GIFCreator()

  # resize gif
  ghis_creator.resize(ghisGIF.size)

  # paste gif
  ghis_creator.paste(ghisGIF, (0,0))

  # get the number of images
  nb_frames = ghis_creator.nbFrames()

  # get a precentage of the frames with the correct text
  half_nb_frames = int(nb_frames / 3)

  # caption text properties
  caption_font_path = os.path.join(os.getcwd(), "resources", "sans_serif.ttf")
  caption_text = TextProperty(backgroundColor=GHIS_CAPTION_BACKGROUND, fontPath=caption_font_path, fontSize=GHIS_FONT_SIZE, color=(255, 255, 255), alignment="center", backgroundMargin=4)

  caption_text.preloadFont()

  for i in range(0, half_nb_frames):
    ghis_creator.seek(i)
    d = ghis_creator.draw()
    ghis_creator.addText(text_properties=caption_text, x=int(ghisGIF.size[0] / 2), y=ghisGIF.size[1] - GHIS_BOTTOM_MARGIN - caption_text.computeSize(d, GHIS_CAPTION)[1], text=GHIS_CAPTION)

  for i in range(half_nb_frames, nb_frames):
    ghis_creator.seek(i)
    d = ghis_creator.draw()
    ghis_creator.addText(text_properties=caption_text, x=int(ghisGIF.size[0] / 2), y=ghisGIF.size[1] - GHIS_BOTTOM_MARGIN - caption_text.computeSize(d, ghis_message)[1], text=ghis_message)

  result = await message.channel.send(f"{message.author.mention} dit:", file=discord.File(ghis_creator.toBuffer(), "ghis.gif"))