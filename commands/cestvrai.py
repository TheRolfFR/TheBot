import discord
import asyncio

import os
from PIL import Image
from PIL import ImageFont, ImageDraw, ImageOps
from io  import BytesIO
import base64

# emojis support feature
import re
# download image from web
import requests

from settings import *

COLOR_FONT = (255, 255, 255, 255)
COLOR_BACKGROUND = (0,0,0,255)

IMAGE_MARGIN = 20

INSIDE_MAX_WIDTH = 1.25 # else 125% of max width
OUTLINE_COLOR = COLOR_FONT # else (255, 255, 255, 255)
OUTLINE_WIDTH = 1

FONT_SIZE_CESTVRAI  = 36
CEST_VRAI_MESSAGE = "C'EST VRAI"

FONT_SIZE_MESSAGE = 22

REACTION_EMOJI = '❌'
REACTION_TIMEOUT = 30.0

def _image_to_discord_file(img, file_name="image", duration=0):
  buffered = BytesIO()

  if isinstance(img, list):
    img[0].save(buffered, format='GIF', save_all=True, append_images=img[1:], optimize=False, loop=0, duration=duration)
  else:
    img.save(buffered, format="PNG")
  
  buffered.seek(0)
  
  final_filename = file_name + (".gif" if isinstance(img, list) else ".png")
  return discord.File(buffered, filename=final_filename)

def _emoji_size(fontSize):
  return int(fontSize * 22 / 16)

def _multiline_text_size(text: str, draw: ImageDraw, font: ImageFont, fontSize):
  lines = text.split("\\n")

  height = 0
  maxWidth = 0

  emojiSize = _emoji_size(fontSize)

  for line in lines:
    # find emojis
    emojis = _p.findall(line)

    # create a pure line
    pureLine = line
    for emojiMatch in emojis:
      pureLine = pureLine.replace(emojiMatch[0], '') # remove da fuck out of the line

    (lineWidth, lineHeight) = draw.textsize(pureLine, font = font)

    # you need to take into account the emojis width
    lineWidth += emojiSize * len(emojis)

    maxWidth = max(maxWidth, lineWidth)
    height += max(emojiSize, lineHeight) if len(emojis) else lineHeight # get max if emojis present in line

  return (maxWidth, height)

_p = re.compile('(<:[^:]+:([0-9]+)>)')
def _drawLine(img: Image.Image, d: ImageDraw, offsetX: int, offsetY: int, line: str, font: ImageFont, fontSize, emojiDict: dict):
  # find emojis
  emojis = _p.findall(line)

  emojiSize = _emoji_size(fontSize)

  (lineWidth, lineHeight) = d.textsize('EXAMPLE', font = font)

  # split line by emojis, really complicated because we need everything
  linearr = []
  linelast = line
  if len(emojis):
    for i in range(len(emojis)):
      explode = linelast.split(emojis[i][0], 1)
      linelast = explode[1]
      linearr.append(explode[0]) # add first part
      linearr.append(int(emojis[i][1])) # add emoji number after
  
  # else there is no emoji just append the line or lastline
  linearr.append(linelast)

  # draw
  for element in linearr:
    if isinstance(element, int):
      if not element in emojiDict:
        # load emoji
        response = requests.get('https://cdn.discordapp.com/emojis/' + str(element) + '.png')
        ori = Image.open(BytesIO(response.content))
        orisize = ori.size
        finalSize = (int(orisize[0]/max(orisize)*emojiSize), int(orisize[1]/max(orisize)*emojiSize))
        emojiDict[element] = ori.resize(finalSize, Image.BICUBIC)

      # paste emoji
      img.paste(emojiDict[element], (int(offsetX), int(offsetY)), emojiDict[element])
      offsetX += emojiSize
    else:
      # it's text
      (lineWidth, lineHeight) = d.textsize(element, font = font)
      d.text((offsetX, offsetY), element, font = font)
      offsetX += lineWidth

  return (offsetY + (max(emojiSize, lineHeight) if len(emojis) else lineHeight), emojiDict)

def openImageFromURL(url):
  response = requests.get(url)
  return Image.open(BytesIO(response.content))

async def cmd_cestvrai(bot: discord.Client, message: discord.Message, command: str, args):
  """Commande meme c'est vrai: `{bot_prefix}cvrai <message d'explication (optionnel)>` + pièce jointe avec image: Affiche l'image dans un cadre avec le message d'explication"""

  # message must have attachment
  if(len(message.attachments) <= 0):
    error = await message.channel.send(
        embed=discord.Embed(
            color=ERROR_COLOR,
            description="Pas d'image en pièce jointe",
        )
    )
    await asyncio.sleep(2)
    await error.delete()
    return

  #define attachment url
  attachment_url = message.attachments[0].url

  #inside image
  try:
    inside = openImageFromURL(attachment_url)
  except:
    error = await message.channel.send(
        embed=discord.Embed(
            color=ERROR_COLOR,
            description="Impossible d'ouvrir le fichier comme image",
        )
    )
    await asyncio.sleep(2)
    await error.delete()
    return

  try:
    animated = inside.n_frames > 1
  except:
    animated = False

  #determine attachment url
  sentence = " "
  if(isinstance(args, list)):
    sentence = " ".join(args)
  elif(isinstance(args, str)):
    sentence = args

  # get rid of spaces
  sentence = sentence.strip()

  # destination image
  dest = Image.new("RGB", (20, 20), COLOR_BACKGROUND)
  d = ImageDraw.Draw(dest)
  
  # font paths
  timesPathBold = os.path.join(os.getcwd(), "resources", "timesbd.ttf")
  timesPath = os.path.join(os.getcwd(), "resources", "times.ttf")

  #fonts
  timesBold = ImageFont.truetype(timesPathBold, FONT_SIZE_CESTVRAI)
  times = ImageFont.truetype(timesPath, FONT_SIZE_MESSAGE)

  # drawings sizes
  (inside_width, inside_height) = inside.size
  (vrai_width, vrai_height) = _multiline_text_size(CEST_VRAI_MESSAGE, d, timesBold, FONT_SIZE_CESTVRAI)
  (message_width, message_height) = _multiline_text_size(sentence, d, times, FONT_SIZE_MESSAGE)

  width = max(inside_width, vrai_width, message_width)

  if animated:
    frames = []
    for i in range(0, inside.n_frames):
      inside.seek(i)

      # appends a copy image
      frames.append(inside.copy())
  
  if(width == inside_width):
    inside_width = min(int(INSIDE_MAX_WIDTH * max(vrai_width, message_width)), inside_width)
    ratio = inside_width / width
    width = inside_width
    inside_height = int(inside_height * ratio)
    if not animated:
      inside = inside.resize((inside_width, inside_height))
    else:
      for i in range(0, len(frames)):
        #resize frame
        frames[i] = frames[i].resize((inside_width, inside_height))
  
  height = inside_height + vrai_height + message_height

  width += 2*IMAGE_MARGIN
  height += 2*IMAGE_MARGIN + int(IMAGE_MARGIN/2)

  if(sentence != ""):
    height += int(IMAGE_MARGIN/2)

  # set correct size
  dest = dest.resize((width, height))

  (coordsY, emojiDictionary) = (IMAGE_MARGIN, {})

  if not animated:
    # paste image
    dest.paste(inside, (int((width - inside_width)/2), IMAGE_MARGIN))
  
  coordsY += inside_height + IMAGE_MARGIN/2

  d = ImageDraw.Draw(dest)

  # white outline
  if not animated:
    d.rectangle([(int((width - inside_width)/2), IMAGE_MARGIN), (int((width + inside_width)/2), IMAGE_MARGIN + inside_height)], None, OUTLINE_COLOR, OUTLINE_WIDTH)

  # draw c'est vrai
  (coordsY, emojiDictionary) = _drawLine(dest, d, (width - vrai_width) / 2, coordsY, CEST_VRAI_MESSAGE, timesBold, FONT_SIZE_CESTVRAI, emojiDictionary)

  # draw message if not empty
  if(sentence != ""):
    coordsY += IMAGE_MARGIN/2

    lines = sentence.split("\\n")
    emojiDictionary = {}
    for line in lines:
      (line_width, line_height) = _multiline_text_size(line, d, times, FONT_SIZE_MESSAGE)
      (coordsY, emojiDictionary) = _drawLine(dest, d, (width - line_width) / 2, coordsY, line, times, FONT_SIZE_MESSAGE, emojiDictionary)

  if(animated):
    duration = inside.info.get("duration", 0)
    images = []

    for i in range(0, len(frames)):
      # create new image
      lastImage = Image.new('RGB', (width, height))

      #paste original image
      lastImage.paste(dest)

      # paste gif frame
      lastImage.paste(frames[i], (int((width - inside_width)/2), IMAGE_MARGIN))
      
      # start drawing
      d = ImageDraw.Draw(lastImage)

      # reput outline
      d.rectangle([(int((width - inside_width)/2), IMAGE_MARGIN), (int((width + inside_width)/2), IMAGE_MARGIN + inside_height)], None, OUTLINE_COLOR, OUTLINE_WIDTH)

      # append to array
      images.append(lastImage.quantize(dither=Image.NONE))
  else:
    duration = 0
    images = dest
  
  await message.delete()
  result = await message.channel.send(f"{message.author.mention} dit:", file=_image_to_discord_file(images, "cestvrai", duration=duration))
  await result.add_reaction(REACTION_EMOJI)
  def check(reaction, user):
    return reaction.message == result and user == message.author and str(reaction.emoji) == REACTION_EMOJI

  try:
    await bot.wait_for('reaction_add', timeout=REACTION_TIMEOUT, check=check)
  except asyncio.TimeoutError:
    await result.remove_reaction(REACTION_EMOJI, bot.user)
  else:
    await result.delete()
