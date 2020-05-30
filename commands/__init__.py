from .botcontrol import cmd_uptime, cmd_ping, cmd_logout
from .translate import cmd_trad
from .moderation import cmd_clear
from .rank import *

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
}
