from commands.player.playersource import *

import discord


class RadioDescription(PlayerSource):
    def __init__(self, display_name: str, url: str, aliases: list, bitrate=None):
        PlayerSource.__init__(self, display_name, url)
        self.aliases = [str(x).lower() for x in aliases]

        before_options = None
        # if bitrate is not None:
        #    before_options = " -b:a " + str(bitrate) + "k "

        self._source = discord.FFmpegPCMAudio(source=self.path, before_options=before_options)

    def source(self):
        return self._source

    def __eq__(self, o):
        """== operator overload"""
        result = False
        if isinstance(o, str):
            result = o in self.aliases

        if result:
            return result

        return super().__eq__(o)

    def __ne__(self, o):
        """!= oeprator overload"""
        return not self.__eq__(o)

    def __str__(self):
        """str() operator overload"""
        return "Nom: ``{0}``, Alias: ``{1}``".format(
            self.display_name, "``, ``".join(self.aliases)
        )
    def url(self):
        return str(self.path)
