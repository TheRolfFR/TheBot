from .botcontrol import cmd_uptime, cmd_ping, cmd_logout
from .translate import cmd_trad
from .moderation import cmd_clear
from .rank import cmd_add_rank, cmd_del_rank, cmd_add_role, cmd_role_info, cmd_rank
from .player import PlayerList
from .player.radio import cmd_radio
from .rank import *
from .stats import cmd_stats, cmd_ranks, cmd_roles
from .games import *
from .mod import cmd_hardlog
from .rename import cmd_rename
from .larousse import cmd_larousse

from .gif.cfaux import cmd_cfaux
from .gif.cvrai import cmd_cvrai
from .gif.ghis import cmd_ghis
from .rageux import cmd_rageux

BOT_COMMANDS = {
    "addrole": cmd_add_role,
    "addrank": cmd_add_rank,
    "clear": cmd_clear,
    "delrank": cmd_del_rank,
    "hardlog": cmd_hardlog,
    "jump": cmd_jump,
    "jumptop": cmd_jump_top,
    "larousse": cmd_larousse,
    "logout": cmd_logout,
    "ping": cmd_ping,
    "radio": cmd_radio,
    "rank": cmd_rank,
    "ranks": cmd_ranks,
    "rename": cmd_rename,
    "roles": cmd_roles,
    "roleinfo": cmd_role_info,
    "stats" : cmd_stats,
    "trad": cmd_trad,
    "uptime": cmd_uptime
}

BOT_SPECIAL_COMMANDS = {
    "cfaux": cmd_cfaux,
    "cvrai": cmd_cvrai,
    "ghis": cmd_ghis,
    "rageux": cmd_rageux
}
