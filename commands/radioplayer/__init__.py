import discord
import asyncio
from .disconnectvocal import disconnectVocal
from .isbotinvocal import isBotInChannel
from .voiceclient import voiceClient

from settings import *

from .radiolist import radioList


def get_channel(client, channel_name):
    for channel in client.get_all_channels():
        if channel.name == channel_name:
            return channel
    return None


class RadioPlayer:
    def __init__(self):
        self.voiceClientSessionID = 0
        self.vc = None

    async def playRadio(self, bot, message, command, args):
        """
    Usage : `{bot_prefix}playRadio <radioName>`
    Joue la radio
    """
    
        # I need a text argument after
        if not (isinstance(args, str) or isinstance(args, list)):
            return

        if not discord.opus.is_loaded():
            discord.opus.load_opus()
        radioName = None
        if isinstance(args, str):
            radioName = args

        if isinstance(args, list):
            radioName = args[0]

        if radioList.get(radioName) is None:
            radiosAvailable = "\n".join(radioList.keys())
            error = await message.channel.send(
                embed=discord.Embed(
                    color=ERROR_COLOR,
                    description=message.author.mention
                    + ", impossible de trouver la radio "
                    + radioName
                    + ". Radios disponibles :\n"
                    + radiosAvailable,
                )
            )
            await asyncio.sleep(2)
            return

        # grab the user who sent the command
        user = message.author

        # if the user is connect in vocal
        # if user not in a channel
        if not user.voice or get_channel(bot, user.voice.channel.name) is None:
            error = await message.channel.send(
                embed=discord.Embed(
                    color=ERROR_COLOR,
                    description=user.mention + ", tu n'es pas dans un channel audio.",
                )
            )
            await asyncio.sleep(2)
            await error.delete()
            return

        voice_channel = get_channel(bot, user.voice.channel.name)

        # if the bot is playing something in the channel
        if not (self.vc is None) and self.vc.channel == user.voice.channel:
            self.vc.stop()
        else:
            # firt deconnect
            await disconnectVocal(bot, message, command, args, self.vc)

            # then reconnect
            self.vc = await voice_channel.connect()
            self.voiceClientSessionID = self.vc.session_id

        # finally you can play
        channel = voice_channel.name
        await message.channel.send(
            embed=discord.Embed(
                color=STATUS_COLOR,
                description="Démarrage de la radio "
                + radioName
                + " dans le channel "
                + channel
                + "...",
            )
        )
        source = radioList.get(radioName)
        print("Playing " + radioName + ": " + source + " in " + channel)

        self.vc.play(
            discord.FFmpegPCMAudio(executable="./database/ffmpeg", source=source)
        )

    async def stopRadio(self, bot, message, command, args):
        """
    Usage : `{bot_prefix}stopRadio [...Disconnect=false]`
    Stop la radio
    """

        # disconnect when the it can
        if not (self.vc is None):
            await self.vc.disconnect()
            self.voiceClientSessionID = 0
            await message.channel.send(
                embed=discord.Embed(
                    color=STATUS_COLOR,
                    description="Bot déconnecté de " + self.vc.channel.name,
                )
            )
            self.vc = None
        else:
            await message.channel.send(
                embed=discord.Embed(
                    color=ERROR_COLOR,
                    description=f":x: OUCH Le bot n'a pas trouvé le salon de la dernière session :x:",
                )
            )
