from data.models import Role, engine
from sqlalchemy.orm import sessionmaker
import discord
from settings import ERROR_COLOR, CONFIRM_COLOR, HELP_COLOR
import re


async def cmd_add_rank(bot, message, command, args):
    """
	Usage : `{bot_prefix}addrank <nom du rang> [couleur hexadécimal]`
	Ajoute un nouveau rang
	"""

    ds_role = discord.utils.get(message.guild.roles, name="lvl 30 SNAIL")

    if ds_role not in message.author.roles:
        await message.channel.send(
            embed=discord.Embed(
                title=f"Aide sur {command}",
                description=f"Vous n'avez pas la permission pour faire cette commande",
                color=ERROR_COLOR,
            )
        )
        return

    Session = sessionmaker(bind=engine)
    session = Session()

    role_name = ""
    role_color = ""
    db_roles = session.query(Role).all()

    pattern = " ([A-Fa-f0-9]{6})$"
    if re.search(pattern, message.content):
        role_color = re.findall(pattern, message.content)[0]
        pattern = "^=addrank (.*) ([A-Fa-f0-9)]{6})?$"
        if not re.search(pattern, message.content):
            await message.channel.send(embed=bot.doc_embed("addrank", ERROR_COLOR))
            return
        role_name = re.findall(pattern, message.content)[0][0]
    else:
        role_color = "dddddd"
        pattern = "^=addrank (.*)"
        if not re.search(pattern, message.content):
            await message.channel.send(embed=bot.doc_embed("addrank", ERROR_COLOR))
            return
        role_name = re.findall(pattern, message.content)[0]

    if role_name not in (_db_roles.name for _db_roles in db_roles):
        db_role = Role(name=role_name, color=role_color, is_rank=True, count=0)
        session.add(db_role)
        session.commit()

    if role_name not in (_ds_roles.name for _ds_roles in message.guild.roles):
        guild = message.guild
        await guild.create_role(
            name=role_name, color=discord.Colour(int(role_color, 16))
        )
        await message.channel.send(
            embed=discord.Embed(
                description=f"{role_name} est désormais disponible", color=CONFIRM_COLOR
            )
        )
    else:
        await message.channel.send(
            embed=discord.Embed(
                description=f"Le rang {role_name} existe déjà", color=ERROR_COLOR
            )
        )

    session.close()


async def cmd_rank(bot, message, command, args):
    """
	Usage : `{bot_prefix}rank <nom du rang>`
	Rejoindre ou partir d'un rang
	"""

    pattern = "^=rank (.*)"
    if not re.search(pattern, message.content):
        await message.channel.send(embed=bot.doc_embed("rank", ERROR_COLOR))
        return

    role_name = re.findall(pattern, message.content)[0]

    Session = sessionmaker(bind=engine)
    session = Session()

    db_role = session.query(Role).filter(Role.name == role_name).first()
    ds_role = discord.utils.get(message.guild.roles, name=role_name)

    if ds_role and db_role.is_rank:
        if ds_role not in message.author.roles:
            await message.author.add_roles(ds_role)
            await message.channel.send(
                embed=discord.Embed(
                    description=f"{message.author.name} fait partie de {role_name}",
                    color=CONFIRM_COLOR,
                )
            )
            db_role.count += 1
            session.commit()
        else:
            await message.author.remove_roles(ds_role)
            await message.channel.send(
                embed=discord.Embed(
                    description=f"{message.author.name} ne fait plus partie de {role_name}",
                    color=CONFIRM_COLOR,
                )
            )
            db_role.count -= 1
            session.commit()
    else:
        await message.channel.send(
            embed=discord.Embed(
                title=f"Aide sur {command}",
                description=f"Le rang {role_name} n'existe pas",
                color=ERROR_COLOR,
            )
        )

    session.close()


async def cmd_ranks(bot, message, command, args):
    """
	Usage : `{bot_prefix}ranks`
	Affiche la liste des rangs
	"""

    if len(args) != 0:
        await message.channel.send(embed=bot.doc_embed("ranks", ERROR_COLOR))
        return

    Session = sessionmaker(bind=engine)
    session = Session()

    db_roles = session.query(Role).filter(Role.is_rank == True).all()
    ds_roles = message.guild.roles
    embed = discord.Embed(title="Rangs disponibles", color=HELP_COLOR)

    for role in ds_roles:
        if role.name in (_db_role.name for _db_role in db_roles):
            embed.add_field(name=role.name, value=len(role.members))

    await message.channel.send(embed=embed)

    session.close()


async def cmd_del_rank(bot, message, command, args):
    """
	Usage : `{bot_prefix}delrank <nom du rang>`
	Supprime un rang
	"""

    ds_role = discord.utils.get(message.guild.roles, name="lvl 30 SNAIL")

    if ds_role not in message.author.roles:
        await message.channel.send(
            embed=discord.Embed(
                title=f"Aide sur {command}",
                description=f"Vous n'avez pas la permission pour faire cette commande",
                color=ERROR_COLOR,
            )
        )
        return

    pattern = "^=delrank (.*)"
    if not re.search(pattern, message.content):
        await message.channel.send(embed=bot.doc_embed("delrank", ERROR_COLOR))
        return

    Session = sessionmaker(bind=engine)
    session = Session()

    role_name = re.findall(pattern, message.content)[0]
    db_role = session.query(Role).filter(Role.name == role_name).first()
    ds_role = discord.utils.get(message.guild.roles, name=role_name)

    if db_role:
        session.delete(db_role)
        session.commit()

    if ds_role:
        await ds_role.delete()
        await message.channel.send(
            embed=discord.Embed(
                description=f"{role_name} est suprimé", color=CONFIRM_COLOR
            )
        )
    else:
        await message.channel.send(
            embed=discord.Embed(
                description=f"Le rang {role_name} n'existe pas", color=ERROR_COLOR
            )
        )

    session.close()


async def cmd_roles(bot, message, command, args):
    """
	Usage : `{bot_prefix}roles`
	Affiche la liste des roles
	"""

    ds_role = discord.utils.get(message.guild.roles, name="lvl 30 SNAIL")

    if ds_role not in message.author.roles:
        await message.channel.send(
            embed=discord.Embed(
                title=f"Aide sur {command}",
                description=f"Vous n'avez pas la permission pour faire cette commande",
                color=ERROR_COLOR,
            )
        )
        return

    if len(args) != 0:
        await message.channel.send(embed=bot.doc_embed("roles", ERROR_COLOR))
        return

    Session = sessionmaker(bind=engine)
    session = Session()

    db_roles = session.query(Role).filter(Role.is_rank == False).all()
    ds_roles = message.guild.roles
    embed = discord.Embed(title="Rangs disponibles", color=HELP_COLOR)

    for role in ds_roles:
        if role.name in (_db_role.name for _db_role in db_roles):
            embed.add_field(name=role.name, value=len(role.members))

    await message.channel.send(embed=embed)

    session.close()


async def cmd_role_info(bot, message, command, args):
    """
	Usage : `{bot_prefix}roleinfo <nom du role>`
	Donne les informations du role
	"""

    ds_role = discord.utils.get(message.guild.roles, name="lvl 30 SNAIL")

    if ds_role not in message.author.roles:
        await message.channel.send(
            embed=discord.Embed(
                title=f"Aide sur {command}",
                description=f"Vous n'avez pas la permission pour faire cette commande",
                color=ERROR_COLOR,
            )
        )
        return

    pattern = "^=roleinfo (.*)"
    if not re.search(pattern, message.content):
        await message.channel.send(embed=bot.doc_embed("roleinfo", ERROR_COLOR))
        return

    Session = sessionmaker(bind=engine)
    session = Session()

    role_name = re.findall(pattern, message.content)[0]
    ds_role = discord.utils.get(message.guild.roles, name=role_name)

    if ds_role:
        embed = discord.Embed(title=f"{role_name}", color=ds_role.colour)
        embed.add_field(name="Nombre de personnes", value=len(ds_role.members))
        embed.add_field(name="Date de création", value=ds_role.created_at)
        await message.channel.send(embed=embed)
    else:
        await message.channel.send(
            embed=discord.Embed(
                description=f"Le role {role_name} n'existe pas", color=ERROR_COLOR
            )
        )

    session.close()


async def cmd_add_role(bot, message, command, args):
    """
	Usage : `{bot_prefix}addrole <nom du role> [couleur hexadécimal]`
	Ajoute un nouveau role
	"""

    ds_role = discord.utils.get(message.guild.roles, name="lvl 30 SNAIL")

    if ds_role not in message.author.roles:
        await message.channel.send(
            embed=discord.Embed(
                title=f"Aide sur {command}",
                description=f"Vous n'avez pas la permission pour faire cette commande",
                color=ERROR_COLOR,
            )
        )
        return

    Session = sessionmaker(bind=engine)
    session = Session()

    role_name = ""
    role_color = ""
    db_roles = session.query(Role).all()

    pattern = " ([A-Fa-f0-9]{6})$"
    if re.search(pattern, message.content):
        role_color = re.findall(pattern, message.content)[0]
        pattern = "^=addrole (.*) ([A-Fa-f0-9)]{6})?$"
        if not re.search(pattern, message.content):
            await message.channel.send(embed=bot.doc_embed("addrole", ERROR_COLOR))
            return
        role_name = re.findall(pattern, message.content)[0][0]
    else:
        role_color = "dddddd"
        pattern = "^=addrole (.*)"
        if not re.search(pattern, message.content):
            await message.channel.send(embed=bot.doc_embed("addrole", ERROR_COLOR))
            return
        role_name = re.findall(pattern, message.content)[0]

    if role_name not in (_db_roles.name for _db_roles in db_roles):
        db_role = Role(name=role_name, color=role_color, is_rank=False, count=0)
        session.add(db_role)
        session.commit()

    if role_name not in (_ds_roles.name for _ds_roles in message.guild.roles):
        guild = message.guild
        await guild.create_role(
            name=role_name, color=discord.Colour(int(role_color, 16))
        )
        await message.channel.send(
            embed=discord.Embed(
                description=f"{role_name} est désormais disponible", color=CONFIRM_COLOR
            )
        )
    else:
        await message.channel.send(
            embed=discord.Embed(
                description=f"Le rang {role_name} existe déjà", color=ERROR_COLOR
            )
        )

    session.close()
