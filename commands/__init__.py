from .botcontrol import cmd_uptime, cmd_ping, cmd_logout
from .translate import cmd_trad
from .moderation import cmd_clear

BOT_COMMANDS = {
	"uptime": cmd_uptime,
	"ping": cmd_ping,
	"logout": cmd_logout,
	"trad": cmd_trad,
	"clear": cmd_clear,
}