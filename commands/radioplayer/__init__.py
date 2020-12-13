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

        bot_vc = self.getBotVoiceClient(message)
        # if the bot is playing something
        if bot_vc:
            # then stop
            bot_vc.stop()

            # if the bot is playing something in another channel
            if bot_vc.channel != user.voice.channel:
                bot_vc.move_to(user.voice.channel)
        else:
            # connect
            try:
                bot_vc = await user.voice.channel.connect() # timeout=10
            except TimeoutError as err:
                await message.channel.send(embed=discord.Embed(color=ERROR_COLOR, description="Timeout connexion"))
                raise err

        # finally you can play
        channel_name = user.voice.channel.name
        await message.channel.send(
            embed=discord.Embed(
                color=STATUS_COLOR,
                description="Démarrage de la radio "
                + radioName
                + " dans le channel "
                + channel_name
                + "...",
            )
        )
        source = radioList.get(radioName)
        print("Playing " + radioName + ": " + source + " in " + channel_name)

        bot_vc.play(
            discord.FFmpegPCMAudio(source=source)
        )

        self.vc = bot_vc

    def getBotVoiceClient(self, message):
        if self.vc is not None:
            return self.vc
        else:
            return message.guild.voice_client

    async def stopRadio(self, bot, message, command, args):
        """
    Usage : `{bot_prefix}stopRadio [...Disconnect=false]`
    Stop la radio
    """
        # get bot voice client
        bot_vc = self.getBotVoiceClient(message)

        # disconnect of voice client
        if bot_vc is not None:
            await bot_vc.disconnect()
            self.vc = None

            await message.channel.send(
                embed=discord.Embed(
                    color=STATUS_COLOR,
                    description="Bot déconnecté de " + bot_vc.channel.name,
                )
            )
        else:
            await message.channel.send(
                embed=discord.Embed(
                    color=ERROR_COLOR,
                    description=f":x: OUCH Le bot n'a pas trouvé le salon de la dernière session :x:",
                )
            )
