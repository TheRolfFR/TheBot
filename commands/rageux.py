import discord
import asyncio

import os
from PIL import Image
from PIL import ImageFont, ImageDraw, ImageOps
from io import BytesIO
import base64

# emojis support feature
import re

# download image from web
import requests

from settings import *

FLAG_HEIGHT = 250  # 250 if full, 179 - cap
FLAG_WIDTH = 284

FLAG_ORIGIN_X = 205
FLAG_ORIGIN_Y = 193

DEFAULT_FONT_SIZE = 40
"""
content  | text | image 
original |  16  | 22
default  | 40   | ?
current  | X    | ?
"""
HORIZONTAL_MARGIN = 40
VERTICAL_MARGIN = 20

_p = re.compile("(<:[^:]+:([0-9]+)>)")


def _emoji_size(fontSize):
    return int(fontSize * 22 / 16)


def _image_to_discord_file(img):
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    buffered.seek(0)

    return discord.File(buffered, filename="rageux.png")


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
            pureLine = pureLine.replace(
                emojiMatch[0], ""
            )  # remove da fuck out of the line

        (lineWidth, lineHeight) = draw.textsize(pureLine, font=font)

        # you need to take into account the emojis width
        lineWidth += emojiSize * len(emojis)

        maxWidth = max(maxWidth, lineWidth)
        height += (
            max(emojiSize, lineHeight) if len(emojis) else lineHeight
        )  # get max if emojis present in line

    return (maxWidth, height)


def _drawLine(
    img: Image.Image,
    d: ImageDraw,
    offsetX: int,
    offsetY: int,
    line: str,
    font: ImageFont,
    fontSize,
    emojiDict: dict,
):
    # find emojis
    emojis = _p.findall(line)

    emojiSize = _emoji_size(fontSize)

    (lineWidth, lineHeight) = d.textsize("EXAMPLE", font=font)

    # split line by emojis, really complicated because we need everything
    linearr = []
    linelast = line
    if len(emojis):
        for i in range(len(emojis)):
            explode = linelast.split(emojis[i][0], 1)
            linelast = explode[1]
            linearr.append(explode[0])  # add first part
            linearr.append(int(emojis[i][1]))  # add emoji number after

    # else there is no emoji just append the line or lastline
    linearr.append(linelast)

    # draw
    for element in linearr:
        if isinstance(element, int):
            if not element in emojiDict:
                # load emoji
                response = requests.get(
                    "https://cdn.discordapp.com/emojis/" + str(element) + ".png"
                )
                ori = Image.open(BytesIO(response.content))
                orisize = ori.size
                finalSize = (
                    int(orisize[0] / max(orisize) * emojiSize),
                    int(orisize[1] / max(orisize) * emojiSize),
                )
                emojiDict[element] = ori.resize(finalSize, Image.BICUBIC)

            # paste emoji
            img.paste(emojiDict[element], (offsetX, offsetY), emojiDict[element])
            offsetX += emojiSize
        else:
            # it's text
            (lineWidth, lineHeight) = d.textsize(element, font=font)
            d.text((offsetX, offsetY), element, font=font)
            offsetX += lineWidth

    return (
        offsetY + (max(emojiSize, lineHeight) if len(emojis) else lineHeight),
        emojiDict,
    )


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

    text = text.strip()

    # open originial image
    image = Image.open(os.path.join(os.getcwd(), "resources", "rageux.jpg"))

    # font path
    fontPath = os.path.join(os.getcwd(), "resources", "sans_serif.ttf")

    # create empty text image
    txt = Image.new("RGBA", image.size)
    d = ImageDraw.Draw(txt)

    # place some text
    fontSize = DEFAULT_FONT_SIZE
    f = ImageFont.truetype(fontPath, fontSize)
    (width, height) = _multiline_text_size(text, d, f, fontSize)
    fontSize = fontSize * (FLAG_WIDTH - HORIZONTAL_MARGIN) // width
    f = ImageFont.truetype(fontPath, fontSize)
    (width, height) = _multiline_text_size(text, d, f, fontSize)
    fontSize = min(fontSize, fontSize * (FLAG_WIDTH - VERTICAL_MARGIN) // height)
    f = ImageFont.truetype(fontPath, fontSize)
    (width, height) = _multiline_text_size(text, d, f, fontSize)

    # compute coords
    coordsX = FLAG_ORIGIN_X - width // 2
    coordsY = FLAG_ORIGIN_Y - height // 2

    # draw text
    lines = text.split("\\n")
    emojiDictionary = {}
    for line in lines:
        (coordsY, emojiDictionary) = _drawLine(
            txt, d, coordsX, coordsY, line, f, fontSize, emojiDictionary
        )

    # rotate text
    textRotated = txt.rotate(45, expand=0, center=(FLAG_ORIGIN_X, FLAG_ORIGIN_Y))

    # paste text on image
    image.paste(textRotated, (0, 0), textRotated)

    await result.delete()
    await message.channel.send(
        f"{message.author.mention} dit:", file=_image_to_discord_file(image)
    )
    return
