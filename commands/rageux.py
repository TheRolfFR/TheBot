import discord
import asyncio

import os
from PIL import Image
from PIL import ImageFont, ImageDraw, ImageOps
from io  import BytesIO
import base64

from settings import *

FLAG_HEIGHT = 250 # 250 if full, 179 - cap
FLAG_WIDTH  = 284

FLAG_ORIGIN_X = 205
FLAG_ORIGIN_Y = 193

DEFAULT_FONT_SIZE = 40
HORIZONTAL_MARGIN = 40
VERTICAL_MARGIN = 20

def _image_to_discord_file(img):
  buffered = BytesIO()
  img.save(buffered, format="PNG")
  buffered.seek(0)
  
  return discord.File(buffered, filename="rageux.png")

def _multiline_text_size(text: str, draw: ImageDraw, font: ImageFont):
  lines = text.split("\\n")

  height = 0
  width = 0

  for line in lines:
    (lineWidth, lineHeight) = draw.textsize(line, font = font)
    width = max(width, lineWidth)
    height += lineHeight

  return (width, height)

async def cmd_rageux(bot: discord.Client, message: discord.Message, command: str, args):
  """Usage : `{bot_prefix}rageux <texte>`
  
  Génère un meme de rageux
	"""

  # I need a text argument after
  if not (isinstance(args, str) or isinstance(args, list)):
    return

  result = await message.channel.send(
      embed=discord.Embed(
          color=STATUS_COLOR,
          description="Création de l'image en cours:...",
      )
  )

  text = ""
  if isinstance(args, list):
    for arg in args:
      text += arg + " "

  # open originial image
  image=Image.open(os.path.join(os.getcwd(), "resources", "rageux.jpg"))

  # create text empty image
  txt=Image.new('RGBA', image.size)
  d = ImageDraw.Draw(txt)

  # font path
  fontPath = os.path.join(os.getcwd(), "resources", "sans_serif.ttf")

  # place some text
  fontSize = DEFAULT_FONT_SIZE
  f = ImageFont.truetype(fontPath, fontSize)
  (width, height) = _multiline_text_size(text, d, font=f)
  fontSize = fontSize * (FLAG_WIDTH - HORIZONTAL_MARGIN)//width;
  f = ImageFont.truetype(fontPath, fontSize)
  (width, height) = _multiline_text_size(text, d, font=f)
  fontSize = min(fontSize, fontSize * (FLAG_WIDTH - VERTICAL_MARGIN)//height)
  f = ImageFont.truetype(fontPath, fontSize)
  (width, height) = _multiline_text_size(text, d, font=f)

  # compute coords
  coordsX = FLAG_ORIGIN_X - width//2
  coordsY = FLAG_ORIGIN_Y - height//2

  # draw text
  lines = text.split("\\n")
  for line in lines:
    d.text((coordsX, coordsY), line,  font=f, fill=(255, 255, 255), align="left")
    coordsY += height//len(lines) # ADD Y COORD AFTER

  # rotate text
  textRotated=txt.rotate(45, expand=0, center=(FLAG_ORIGIN_X, FLAG_ORIGIN_Y))

  # paste text on image
  image.paste(textRotated, (0, 0), textRotated)

  await result.delete()
  await message.channel.send(file=_image_to_discord_file(image))
  return
