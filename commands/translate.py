import discord
import googletrans

from data import *


def fix_flag(dest):
	if dest in flag_emotes_fixes:
		return flag_emotes_fixes[dest]
	else:
		return dest

def fix_source(src):
	if src == "cafr": return "fr"
	else: return src

async def cmd_trad(bot, message, command, args):
	"""
	Usage : `{bot_prefix}trad [-<code langue>] <texte à traduire>`
	Traduit du texte.
	Exemples :
	`{bot_prefix}trad Texte en français` : Traduit le français en anglais par défaut
	`{bot_prefix}trad Text in another language` : Traduit les autres langues en français par défaut
	`{bot_prefix}trad -de Texte` : Traduit dans une autre langue (utilisez un code à deux lettres comme sur https://fr.wikipedia.org/wiki/Liste_des_codes_ISO_639-1)
	"""
	if len(args) == 0:  # Requête vide
		await message.channel.send(embed=bot.doc_embed("trad", error_color))
		return
	
	translator = googletrans.Translator()
	
	if args[0].startswith("-"):  # Argument pour la langue de destination
		text = message.content[len(bot.prefix) + len(command) + 1:].partition(" ")[2].strip()
		if text == "":
			await message.channel.send(embed=bot.doc_embed("trad", error_color))
			return
		destination = args[0].strip("-")
		if destination not in googletrans.LANGUAGES:
			await message.channel.send(embed=discord.Embed(color=error_color, description="Code de langue invalide. Les codes sont des codes à 2 lettres comme donnés sur https://fr.wikipedia.org/wiki/Liste_des_codes_ISO_639-1"))
			return
		source = translator.detect(text)
		
	else:
		text = message.content[len(bot.prefix) + len(command) + 1:]
		source = translator.detect(text)
		destination = "en" if fix_source(source.lang) == "fr" else "fr"
	srclang = fix_source(source.lang)
	translation = translator.translate(text, src=srclang, dest=destination)
	embed = discord.Embed(title=message.author.name, color=help_color, description=f":flag_{fix_flag(srclang)}:->:flag_{fix_flag(destination)}:  {translation.text}")
	embed.set_footer(text=translation.origin)
	await message.channel.send(embed=embed)
	await message.delete()