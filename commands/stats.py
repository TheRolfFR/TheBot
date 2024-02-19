import discord
import asyncio
from datetime import datetime
from settings import *
import csv
import io


def _dict_to_csv_discord_file(dict, filename):
    result = []
    for key in dict.keys():
        if isinstance(dict[key], list):
            for value in dict[key]:
                result.append([str(key), str(value)])
        else:
            result.append([str(key), str(dict[key])])

    writer_file = io.StringIO()
    writer = csv.writer(writer_file, dialect="excel", delimiter=",")

    for line in result:
        writer.writerow(line)

    writer_file.seek(0)

    return discord.File(
        writer_file,
        filename=f"{filename} { datetime.now().strftime('%Y-%m-%d %Hh%Mm%Ss') }.csv",
    )


async def cmd_stats(
    bot: discord.Client, message: discord.Message, command: str, args: any
):
    """Donner toutes les stats du serveurs"""

    # get guild
    guild: discord.Guild = message.guild

    # message must have a guild
    if guild is None:
        return

    # add wait message
    waitMessage = await message.channel.send(
        embed=discord.Embed(
            title="Création des stats en cours...",
            description="Merci de patienter...",
            color=HELP_COLOR,
        )
    )

    # create result embed
    resultEmbed = discord.Embed(
        title=f"Stats du serveur {guild.name}",
        description="Statistiques du serveur au " + datetime.now().strftime("%d/%m/%Y"),
        color=HELP_COLOR,
    )
    resultEmbed.set_thumbnail(url=guild.icon.url) # 'Guild' object has no attribute 'icon_url'

    # add owner
    resultEmbed.add_field(
        name="Propriétaire", value=guild.owner.display_name, inline=False
    )

    # add creation date
    resultEmbed.add_field(
        name="Date de création",
        value=guild.created_at.strftime("%d/%m/%Y %H:%M:%S"),
        inline=False,
    )

    # members count
    resultEmbed.add_field(
        name="Nombre de membres", value=str(guild.member_count), inline=False
    )

    # sort roles and ranks
    guild_roles = guild.roles
    roles = []
    ranks = []
    for r in guild_roles:
        if r.name != "@everyone":
            if r.hoist:
                roles.append(r.name)
            else:
                ranks.append(r.name)

    # add roles
    resultEmbed.add_field(
        name="Roles", value="​" + ", ".join(roles), inline=False
    )  # the "" \u200 is a zero width space to avoid empty value
    # add ranks
    resultEmbed.add_field(
        name="Ranks", value="​" + ", ".join(ranks), inline=False
    )  # the "" \u200 is a zero width space to avoid empty value

    # get all members arrival dates
    memberArrivals = {}
    for member in guild.members:
        memberArrivals[member.name] = str(member.joined_at)

    # send final message
    await message.channel.send(
        embed=resultEmbed, file=_dict_to_csv_discord_file(memberArrivals, "members")
    )
    # delete the last message
    await waitMessage.delete()

    await cmd_roles(bot, message, command, args)
    await cmd_ranks(bot, message, command, args)


async def cmd_roles(
    bot: discord.Client, message: discord.Message, command: str, args: any
):
    """Liste la role des roles"""
    guild = message.guild

    # message must have a guild
    if guild is None:
        return

    # sort roles and ranks
    guild_roles = guild.roles
    roles = []
    ranks = []
    for r in guild_roles:
        if r.hoist:
            roles.append(r)
        else:
            ranks.append(r)

    # get roles lists
    membersRoles = {}
    for r in roles:
        if r.name != "@everyone":
            membersRoles[r.name] = []

    # get all ranks and roles in members
    for member in guild.members:
        for r in member.roles:
            if r.name != "@everyone" and r in roles:
                membersRoles[r.name].append(member.name)

    # print(membersRoles)

    # filter bots
    keys = list(membersRoles.keys())
    for r in keys:
        if len(membersRoles[r]) == 1 and membersRoles[r][0] == r:
            membersRoles.pop(r, None)

    resultEmbed = discord.Embed(
        title=f"Roles du serveur {guild.name}",
        description="Roles du serveur au " + datetime.now().strftime("%d/%m/%Y"),
        color=HELP_COLOR,
    )
    resultEmbed.set_thumbnail(url=guild.icon.url)

    for roleName in membersRoles.keys():
        resultEmbed.add_field(name=roleName, value=str(len(membersRoles[roleName]))[:25])
    await message.channel.send(
        embed=resultEmbed, file=_dict_to_csv_discord_file(membersRoles, "roles")
    )


async def cmd_ranks(
    bot: discord.Client, message: discord.Message, command: str, args: any
):
    """Liste la role des ranks"""

    guild = message.guild

    # message must have a guild
    if guild is None:
        return

    # sort roles and ranks
    guild_roles = guild.roles
    roles = []
    ranks = []
    for r in guild_roles:
        if r.hoist:
            roles.append(r)
        else:
            ranks.append(r)

    # get ranks lists
    membersRanks = {}
    for r in ranks:
        if r.name != "@everyone":
            membersRanks[r.name] = []

    # get all ranks and roles in members
    for member in guild.members:
        for r in member.roles:
            if r.name != "@everyone" and r in ranks:
                membersRanks[r.name].append(member.name)

    # print(membersRanks)

    # filter bots
    keys = list(membersRanks.keys())
    for r in keys:
        if len(membersRanks[r]) == 1 and r == membersRanks[r][0]:
            membersRanks.pop(r, None)

    resultEmbed = discord.Embed(
        title=f"Ranks du serveur {guild.name}",
        value="Roles du serveur au " + datetime.now().strftime("%d/%m/%Y"),
        color=HELP_COLOR,
    )
    resultEmbed.set_thumbnail(url=guild.icon_url)

    for roleName in membersRanks.keys():
        resultEmbed.add_field(name=roleName, value=str(len(membersRanks[roleName])))
    await message.channel.send(
        embed=resultEmbed, file=_dict_to_csv_discord_file(membersRanks, "ranks")
    )
