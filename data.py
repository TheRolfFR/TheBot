bot_prefix = "="

help_color = 0x55AAFF
error_color = 0xFF4406

docs = {
	"uptime": f"Usage : `{bot_prefix}uptime`\nRenvoie le temps écoulé depuis le lancement du bot",
	"clear": f"Usage : `{bot_prefix}clear <nombre de messages à supprimer>`\nSupprime les derniers messages",
	"logout": f"Usage : `{bot_prefix}logout`\nDéconnecte le bot",
	"ping": f"Usage : `{bot_prefix}ping`\nRenvoie la latence du bot",
	"help": f"Usage : `{bot_prefix}help <commande>`\nDonne de l’aide sur une commande",
	"trad": f"Usage : `{bot_prefix}trad [-<code langue>] <texte à traduire>`\nTraduit du texte.\nExemples :\n`{bot_prefix}trad Texte en français` : Traduit le français en anglais par défaut\n`{bot_prefix}trad Text in another language` : Traduit les autres langues en français par défaut\n`{bot_prefix}trad -de Texte` : Traduit dans une autre langue (utilisez un code à deux lettres comme sur https://fr.wikipedia.org/wiki/Liste_des_codes_ISO_639-1)", 
}

flag_emotes_fixes = {
	"af": "za", "am": "et", "be": "by", "bn": "bg", "bs": "ba", "ca": "white", "ceb": "ph", "co": "white", "cs": "cz",
	"da": "dk", "eo": "white", "ny": "mw", "ar": "sa", "fy": "white", "gl": "white", "ka": "ge", "en": "gb", "et": "ee",
	"eu": "white", "hy": "am", "sq": "al", "sv": "se", "tl": "ph", "zh-cn": "cn", "zh-tw": "tw", "el": "gr", "gu": "in",
	"ha": "ne", "haw": "white", "iw": "il", "hi": "in", "hmn": "white", "ig": "ng", "ga": "ie", "jw": "id", "kn": "in",
	"kk": "kz", "km": "kh", "ko": "kr", "ku": "white", "ky": "kg", "la": "lo", "la": "white", "lb": "lu", "ms": "my", "ml": "in",
	"mi": "nz", "mr": "in", "my": "mm", "ne": "np", "ps": "af", "fa": "ir", "pa": "in", "sm": "ws", "gd": "white", "sr": "rs",
	"st": "ls", "sn": "zw", "sd": "pk", "si": "lk", "sl": "si", "su": "sd", "sw": "ke", "tg": "tj", "tm": "in", "te": "in", 
	"uk": "ua", "ur": "pk", "vi": "vn", "cy": "white", "xh": "za", "yi": "white", "yo": "bj", "zu": "za", "fil": "ph", "he": "il",
}