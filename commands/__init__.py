from .botcontrol import cmd_uptime, cmd_ping, cmd_logout
from .translate import cmd_trad
from .moderation import cmd_clear
from .rank import cmd_add_rank, cmd_del_rank, cmd_add_role, cmd_role_info, cmd_rank
from .radio import Radio
from .rank import *
from .stats import cmd_stats, cmd_ranks, cmd_roles
from .games import *
from .mod import cmd_hardlog

laRadio = Radio()

BOT_COMMANDS = {
    "addrole": cmd_add_role,
    "addrank": cmd_add_rank,
    "clear": cmd_clear,
    "delrank": cmd_del_rank,
    "hardlog": cmd_hardlog,
    "jump": cmd_jump,
    "jumptop": cmd_jump_top,
    "logout": cmd_logout,
    "ping": cmd_ping,
    "radio": laRadio.cmd_radio,
    "rank": cmd_rank,
    "ranks": cmd_ranks,
    "roles": cmd_roles,
    "roleinfo": cmd_role_info,
    "stats" : cmd_stats,
    "trad": cmd_trad,
    "uptime": cmd_uptime
}
