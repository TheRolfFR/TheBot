import discord
from discord.utils import get
from random import random
from os import makedirs
from os.path import abspath, join, dirname
from settings import *
import asyncio
import json

JUMP_TOP_FILENAME = "jump_top.json"

def guild_data_location(guild_id: int):
    """path be like /data/<id_server>/jumptop.json"""

    # go to dir(file)/
    # => /commands/games/

    # go to dir(file)/../
    # => /commands/
    
    # go to dir(file)/../../ 
    # => /
    
    # go to dir(file)/../../data/
    # => /data/
    
    # go to dir(file)/../../data/<id_server>/
    # => /data/<id_server>/

    return abspath(join(dirname(__file__), '..', '..', 'data', str(guild_id)))

jumpTop = {}
current_jumps = {}

JUMP_CHANCE = 0.75
JUMP_TOP_DISPLAY = 20

def open_jump_top(guild_id: int):
    data_location = guild_data_location(guild_id)
    jump_top_location = join(data_location, JUMP_TOP_FILENAME)
    
    server_jump_top = {}

    # noinspection PyBroadException
    try:
        makedirs(data_location, exist_ok = True)
        f = open(jump_top_location, 'r')
        raw = f.read()
        f.close()

        j = json.loads(raw)
        if isinstance(j, dict):
            server_jump_top = j
    except Exception:
        pass

    return server_jump_top

def write_jump_file(guild_id: int, jump_top: dict):
    data_location = guild_data_location(guild_id)

    try:
        makedirs(data_location, exist_ok = True)

        f = open(join(data_location, JUMP_TOP_FILENAME), 'w')
        f.write(json.dumps(jump_top))
        f.flush()
        f.close()
    except Exception:
        pass

# noinspection PyUnusedLocal
async def cmd_jump(bot: discord.Client, message: discord.Message, command: str, args):
    """Jeu du jump, soit tu sautes soit tu plonges!"""

    guild = message.guild

    if guild is None:
        return

    # else get the guild ID and store it
    guild_id = str(guild.id)
    author_id = str(message.author.id)

    # get or add the key
    if guild_id not in jumpTop:
        jumpTop[guild_id] = open_jump_top(guild_id)

    if guild_id not in current_jumps:
        current_jumps[guild_id] = {}

    if author_id not in jumpTop[guild_id]:
        jumpTop[guild_id][author_id] = 0

    if author_id not in current_jumps[guild_id]:
        current_jumps[guild_id][author_id] = 0

    probability = random()
    if probability < JUMP_CHANCE:
        current_jumps[guild_id][author_id] += 1

        if current_jumps[guild_id][author_id] > jumpTop[guild_id][author_id]:
            jumpTop[guild_id][author_id] = current_jumps[guild_id][author_id]

            write_jump_file(guild_id=guild_id, jump_top=jumpTop[guild_id])

        await message.channel.send(embed=discord.Embed(
            title="Tu as réussi ton jump!",
            description=f"Bravo {message.author.mention} ! Tu passes à **{str(current_jumps[guild_id][author_id])}** !",
            color=CONFIRM_COLOR))
    else:
        current_jumps[guild_id][author_id] = 0
        await message.channel.send(embed = discord.Embed(
            title="Tu as raté ton jump!",
            description=f"Plouf, {message.author.mention} ! Tu retombes à **0** :cry:",
            color=ERROR_COLOR))

async def cmd_jump_top(bot: discord.Client, message: discord.Message, command: str, args):
    """Leaderboard du jeu jump"""

    guild = message.guild

    if guild is None:
        return

    # else get the guild ID and store it
    guild_id = str(guild.id)
    author_id = str(message.author.id)

    # get or add the key
    if guild_id not in jumpTop:
        jumpTop[guild_id] = open_jump_top(guild_id)

    # get list of top sorted by decending 
    topListSorted = list({k: v for k, v in sorted(jumpTop[guild_id].items(), key=lambda item: item[1])[::-1]}.items())
    finalString = "Aucun joueurs"

    resultEmbed = discord.Embed(title="Jump leaderboard (" + str(len(topListSorted)) + " joueur" + ("s" if len(topListSorted) > 1 else "") + ")", color=0xD50000)
    
    i = 0
    for top in topListSorted[:3]:
        resultEmbed.add_field(name="TOP " + str(i+1), value=str(topListSorted[i][1]) + " pt(s) : " + guild.get_member(int(topListSorted[i][0])).display_name, inline=False)
        i += 1

    if len(topListSorted):
        finalString  = ''
    
    for i , top_value in enumerate(topListSorted[:JUMP_TOP_DISPLAY]) :
        if i > 2:
            finalString += str(topListSorted[i][1]) + " pt" + ("s" if topListSorted[i][1] > 1 else "") + " : " + guild.get_member(int(topListSorted[i][0])).display_name + "\n"

    # your rank
    authorRankList = [idx for idx, key in enumerate(topListSorted) if key[0] == author_id]
    
    # authorRank = authorRankList[0] # index
    if len(authorRankList) and authorRankList[0] >= JUMP_TOP_DISPLAY:
        finalString += "...\n" + str(topListSorted[authorRankList[0]][1]) + " pt" + ("s" if topListSorted[authorRankList[0]][1] > 1 else "") + " : " + guild.get_member(int(topListSorted[authorRankList[0]][0])).display_name

    if(len(finalString)):
        resultEmbed.add_field(name="Suite top " + str(JUMP_TOP_DISPLAY), value=finalString, inline=False)

    await message.channel.send(embed=resultEmbed)