from typing import List, Tuple
import discord  # type: ignore
import asyncio

# path things
import os
import PIL
from PIL import ImageSequence

from .gifcreator import GIFCreator
from .gifcreator.text_property import TextProperty

RED_COLOR = (249, 0, 16, 255)
FONT_SIZE = 38

WAIT_EMOJI = "⏳"
DELETE_EMOJI = "🗑️"
DELETE_TIMEOUT = 30.0

BACKGROUND_PATH = os.path.join(os.getcwd(), "resources", "not_normal.gif")
RED_DOTS_PATH = os.path.join(os.getcwd(), "resources", "not_normal_red_dot.gif")

# preload background
bg_gif = GIFCreator.loadImageFromPath(BACKGROUND_PATH)
# gif creator preloaded
bg_gif_creator = GIFCreator()
bg_gif_creator.resize(bg_gif.size)
bg_gif_creator.paste(bg_gif, (0, 0))

# * ---------- RED DOTS LOCATION ----------
RedDotsLocation = []
RedDotsFound = 0
RedDotsLen = 0


def determineLocation():
    print("Finding Red dots location... ", end="", flush=True)

    global RedDotsLocation
    global RedDotsFound
    global RedDotsLen
    if len(RedDotsLocation) != 0:
        return

    redDotsImage = GIFCreator.loadImageFromPath(RED_DOTS_PATH)
    RedDotsLen = redDotsImage.n_frames
    [width, height] = redDotsImage.size
    RedDotsLocation = [None] * 44
    for i in range(44, RedDotsLen):
        redDotsImage.seek(i)

        pixel_position = None

        row = 0
        while pixel_position is None and row < height:
            col = 0
            while pixel_position is None and col < width:
                pixel = redDotsImage.getpixel((col, row))
                if type(pixel) == tuple and pixel == RED_COLOR:
                    pixel_position = [col + 1, row + 1]
                    RedDotsFound += 1

                col += 1
            row += 1
        RedDotsLocation.append(pixel_position)

    # make sure we didn't mess us
    assert len(RedDotsLocation) == RedDotsLen
    print(f"✅ {RedDotsFound}/" + str(len(RedDotsLocation)))


# determineLocation()
RedDotsLocation = [None] * 44 + [
    [203, 30],
    [203, 33],
    [200, 30],
    [196, 18],
    [194, 19],
    [193, 24],
    [198, 20],
    [196, 21],
    [196, 24],
    [188, 26],
    [185, 25],
    [176, 30],
    [162, 38],
    [157, 42],
    [156, 44],
    [164, 43],
]
# print(RedDotsLocation)

caption_font_path = os.path.join(os.getcwd(), "resources", "seguibl.ttf")
# caption text properties
caption_text = TextProperty(
    fontPath=caption_font_path,
    fontSize=FONT_SIZE,
    color=(255, 255, 255),
    alignment="center",
    preloadFont=True,
    backgroundMargin=4,
    stroke_width=2,
    stroke_fill=(0, 0, 0),
)

# preload font for performances
caption_text.preloadFont()


async def cmd_just_be_normal(
    bot: discord.Client, message: discord.Message, _command: str, args
):
    """
    GIF creator: Why can't you just be normal
    ``{bot_prefix}normal message`` Affiche un gif du ghis
    L'auteur peut réagir avec 🗑 pour supprimer le gif jusqu'à 30s après la publication du GIF
    """
    # please wait
    await message.add_reaction(WAIT_EMOJI)

    # MESSAGE, ASSEMBLE!
    full_message = " ".join(args)

    # create new ghis with correct size
    gif_creator = GIFCreator()
    gif_creator.resize(bg_gif.size)

    # paste gif
    gif_creator.paste(bg_gif_creator, (0, 0))

    points = [(i, pos) for [i, pos] in enumerate(RedDotsLocation) if pos]
    for [i, pos] in points:
        # custom message part
        gif_creator.seek(i)
        d = gif_creator.draw()
        text_height = caption_text.computeSize(d, full_message)[1]
        gif_creator.addText(
            caption_text, pos[0], pos[1] - text_height / 2, full_message
        )

    # send the result
    result = await message.channel.send(
        f"{message.author.mention} dit:",
        file=discord.File(gif_creator.toBuffer(), "just_be_normal.gif"),
        reference=message,
        mention_author=False,
    )
    await message.remove_reaction(WAIT_EMOJI, bot.user)

    # * delete part
    await result.add_reaction(DELETE_EMOJI)

    def check(reaction, user):
        return (
            reaction.message == result
            and user == message.author
            and str(reaction.emoji) == DELETE_EMOJI
        )

    try:
        await bot.wait_for("reaction_add", timeout=DELETE_TIMEOUT, check=check)
    except asyncio.TimeoutError:
        await result.remove_reaction(DELETE_EMOJI, bot.user)
    else:
        try:
            await message.delete()
            await result.delete()
        except:
            pass
