from .botcontrol import cmd_uptime, cmd_ping, cmd_logout
from .translate import cmd_trad
from .moderation import cmd_clear
from .rank import cmd_add_rank, cmd_del_rank, cmd_add_role, cmd_role_info, cmd_rank
from .rageux import cmd_rageux
from .radioplayer import RadioPlayer
from .radioplayer.disconnectvocal import disconnectVocal
from .rank import *
from .stats import cmd_stats, cmd_ranks, cmd_roles

radio = RadioPlayer()

BOT_COMMANDS = {
    "uptime": cmd_uptime,
    "ping": cmd_ping,
    "logout": cmd_logout,
    "trad": cmd_trad,
    "clear": cmd_clear,
    "addrank": cmd_add_rank,
    "rank": cmd_rank,
    "ranks": cmd_ranks,
    "delrank": cmd_del_rank,
    "roles": cmd_roles,
    "roleinfo": cmd_role_info,
    "addrole": cmd_add_role,
    "rageux": cmd_rageux,
    "playRadio": radio.playRadio,
    "stopRadio": radio.stopRadio,
    "disconnectVocal": disconnectVocal,
    "stats" : cmd_stats
}
