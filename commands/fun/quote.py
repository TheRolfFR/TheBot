import os
from settings import *

import tempfile

import discord
import asyncio
from moviepy.editor import *

WIDTH=round(4/3*200) # 480
HEIGHT=200 # 270
SCREENSIZE = (WIDTH,HEIGHT)

QUOTE_TEXT_SIZE = 25 # 25
AUTHOR_TEXT_SIZE = 18 # 18

DURATION = 8

REACTION_EMOJI = '🗑'
REACTION_TIMEOUT = 30.0

def split_line_by_width(line, width, font, fontsize):
    words = line.split()
    result = []
    current_line = words[0]
    previous_line = current_line
    previous_width = 0
    for word in words[1:]:
        text_clip = TextClip(current_line,color='white', font=font, fontsize=fontsize)
        text_size = text_clip.size
        text_clip.close()
        
        if previous_width <= width and text_size[0] <= width:
            previous_line = current_line
            previous_width = text_size[0]
            current_line += " " + word
        else:
            result.append(previous_line.strip())
            current_line = word
            previous_line = word
            previous_width = 0
    if current_line:
        result.append(current_line.strip())

    res = "\n".join(result)
    return str(res)

async def cmd_quote(bot, message, command, args):
    """
	Usage : `{bot_prefix}quote <quote> [--author <author>]`
	Monte une vidéo de citation sur fond de musique classique
	"""
    await message.add_reaction("🎬")

    if isinstance(args, str):
        args = [args]
    args = " ".join(args)

    # quote defaults to the whole sentence
    quote = args.strip()
    # author defaults to author
    author = message.author.name.strip()

    if "--author" in args:
        splitted = args.split("--author")
        quote = splitted[0].strip()
        author = splitted[1].strip()

    # do not allow empty quote nor author
    if quote == "" or author == "":
        return

    quote = '“' + quote + '”'
    quote = quote.replace("\\n", "\n")

    #* Create clips
    quote = split_line_by_width(quote, WIDTH, "Times-New-Roman-Italic", QUOTE_TEXT_SIZE)
    quoteTextClip = TextClip(quote,color='white', font="Times-New-Roman-Italic", fontsize=QUOTE_TEXT_SIZE)
    
    nameTextClip = TextClip(author, color='white', font='Times-New-Roman', fontsize=AUTHOR_TEXT_SIZE)
    cutAudioClip: AudioFileClip = AudioFileClip(os.path.join(os.getcwd(), "resources", "vivaldi_4_saisons.wav")).subclip(0,DURATION)
    quoteTextClip.audio = cutAudioClip

    compositeClip: CompositeVideoClip = CompositeVideoClip( [quoteTextClip.set_pos('center'), nameTextClip.set_pos(("right","bottom"))],
        size=SCREENSIZE).subclip(0,DURATION)
    clips = [compositeClip]
    
    await message.clear_reaction("🎬")

    #* Save
    await message.add_reaction("💾")

    #* Open and close file pointer as quick as possible
    fp = tempfile.TemporaryFile(prefix='quote-', suffix='.mp4')
    finalClipPath = str(fp.name)
    fp.close()

    finalClipName = os.path.basename(finalClipPath)
    
    finalClip = concatenate_videoclips(clips)
    finalClip.write_videofile(finalClipPath, fps=25, codec='mpeg4', verbose= False, logger= None)

    # close all
    quoteTextClip.close()
    nameTextClip.close()
    compositeClip.close()
    cutAudioClip.close()
    finalClip.close()

    await message.clear_reaction("💾")
    
    await message.add_reaction("⬆️")
    result = await message.channel.send(f"{message.author.mention} cite:", file=discord.File(open(finalClipPath, "rb"), filename=finalClipName))
    await message.clear_reaction("⬆️")

    await result.add_reaction(REACTION_EMOJI)
    def check(reaction, user):
        return reaction.message == result and user == message.author and str(reaction.emoji) == REACTION_EMOJI

    try:
        await bot.wait_for('reaction_add', timeout=REACTION_TIMEOUT, check=check)
    except asyncio.TimeoutError:
        await result.remove_reaction(REACTION_EMOJI, bot.user)
    else:
        await result.delete()

    await asyncio.sleep(1)
    os.remove(finalClipPath)
