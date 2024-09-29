from commands.player.playersource import PlayerSource

import discord
import requests


class RadioDescription(PlayerSource):
    def __init__(self, display_name: str, url: str, aliases: list, bitrate=None):
        super().__init__(display_name, path=url)
        self.aliases = [str(x).lower() for x in aliases]

        before_options = None
        # if bitrate is not None:
        #    before_options = " -b:a " + str(bitrate) + "k "

        self._source = discord.FFmpegPCMAudio(
            source=self.path, before_options=before_options
        )

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
        return (
            f"Nom: ``{self.display_name}``"
            f", Alias: ``{'``, ``'.join(self.aliases)}``"
        )

    def __repr__(self) -> str:
        return self.__str__()

    def status(self) -> str:
        """Get radio HTTP link"""
        try:
            r = requests.get(self.url, timeout=3, stream=True)
            code = str(r.status_code)
        except (requests.ReadTimeout, requests.ConnectionError):
            code = "ERR"
        return code

    @property
    def url(self):
        return str(self.path)
