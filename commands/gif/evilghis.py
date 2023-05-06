import discord
import asyncio

# path things
import os

from .gifcreator import GIFCreator
from .gifcreator.text_property import TextProperty

GHIS_CAPTION = "Et que meure"
GHIS_CAPTION_PADDING = 6
GHIS_CAPTION_BACKGROUND = (0, 0, 0, int(20))
GHIS_FONT_SIZE = 52
GHIS_BOTTOM_MARGIN = 20

WAIT_EMOJI = "⏳"

DELETE_EMOJI = "🗑"
DELETE_TIMEOUT = 30.0

pathGIFGhis = os.path.join(os.getcwd(), "resources", "ghis.gif")
ghisGIF = GIFCreator.loadImageFromPath(pathGIFGhis)

# ghis creator preloaded
evilGhisGIFCreator = GIFCreator()
evilGhisGIFCreator.resize(ghisGIF.size)
evilGhisGIFCreator.paste(ghisGIF, (0, 0))

# getting frames count
nb_frames = evilGhisGIFCreator.nbFrames()
half_nb_frames = int(nb_frames / 3)

caption_font_path = os.path.join(os.getcwd(), "resources", "sans_serif.ttf")
# caption text properties
caption_text = TextProperty(
    backgroundColor=GHIS_CAPTION_BACKGROUND,
    fontPath=caption_font_path,
    fontSize=GHIS_FONT_SIZE,
    color=(255, 255, 255),
    alignment="center",
    backgroundMargin=4,
)

# preload font for performances
caption_text.preloadFont()

# start of message
for i in range(0, half_nb_frames):
    evilGhisGIFCreator.seek(i)
    d = evilGhisGIFCreator.draw()
    evilGhisGIFCreator.addText(
        text_properties=caption_text,
        x=int(ghisGIF.size[0] / 2),
        y=ghisGIF.size[1]
        - GHIS_BOTTOM_MARGIN
        - caption_text.computeSize(d, GHIS_CAPTION)[1],
        text=GHIS_CAPTION,
    )


async def cmd_evilghis(
    bot: discord.Client, message: discord.Message, command: str, args
):
    """
    Commande des meilleurs morts du evil ghis
    ``{bot_prefix}evilghis l'UTBiscord`` Affiche un gif du ghis
    L'auteur peut réagir avec 🗑 pour supprimer le gif jusqu'à 30s après la publication du GIF
    """
    # please wait
    await message.add_reaction(WAIT_EMOJI)

    # MESSAGE, ASSEMBLE!
    ghis_message = " ".join(args)

    # create new ghis with correct size
    ghis_creator = GIFCreator()
    ghis_creator.resize(ghisGIF.size)

    # paste gif
    ghis_creator.paste(evilGhisGIFCreator, (0, 0))

    # custom message part
    for i in range(half_nb_frames, nb_frames):
        ghis_creator.seek(i)
        d = ghis_creator.draw()
        ghis_creator.addText(
            text_properties=caption_text,
            x=int(ghisGIF.size[0] / 2),
            y=ghisGIF.size[1]
            - GHIS_BOTTOM_MARGIN
            - caption_text.computeSize(d, ghis_message)[1],
            text=ghis_message,
        )

    # invert gif
    for i in range(0, nb_frames):
        ghis_creator.seek(i)
        ghis_creator.invert()

    # send the result
    result = await message.channel.send(
        f"{message.author.mention} dit:",
        file=discord.File(ghis_creator.toBuffer(), "ghis.gif"),
    )
    await message.remove_reaction(WAIT_EMOJI, bot.user)

    # delete part
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
