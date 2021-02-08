import discord
import asyncio

from settings import *

from .radiodescription import RadioDescription
from .radioplayer import RadioPlayer
from os.path import join, dirname

RADIO_LIST_PATH = join(dirname(__file__), 'radiolist.py')

def get_radio_list():
    """Dynamically imports radio list"""

    exec(open(RADIO_LIST_PATH).read())

    return locals()['radioList']

class Radio:
    """Radio command"""
    players: list = []

    def find_radio(self, alias: str):
        """Find radio description if"""

        # hot loading
        radioList = get_radio_list()

        result = None
        i = 0
        while i < len(radioList) and result is None:
            if radioList[i] == alias:
                result = radioList[i]
            
            i += 1
        
        return result

    def get_player(self, guild: discord.Guild):
        """Get or create player for guild"""
        result = None
        i = 0
        while i < len(self.players) and result is None:
            if self.players[i].guild == guild:
                result = self.players[i]
            
            i += 1

        """No result found, create"""
        if result is None:
            result = RadioPlayer(guild=guild)
            self.players.append(result)
        
        return result

    async def cmd_radio(self, bot: discord.Client, message: discord.Message, command: str, args: list):
        """
        `{bot_prefix}radio` : affiche la liste des radios
        `{bot_prefix}radio list` : affiche la liste des radios
        `{bot_prefix}radio play <radioAlias>` : Joue une radio
        `{bot_prefix}radio playing` : Indique quelle radio est jouée
        `{bot_prefix}radio pause`: met en pause la radio
        `{bot_prefix}radio resume` : rejoue la radio
        `{bot_prefix}radio stop` : stop la radio
        `{bot_prefix}radio volume <volume [0:100]>` : Change le volume de la radio
        """
        if not args: # if no args list radios
            theList = "**Liste des radios :**"

            # hot loading
            radioList = get_radio_list()

            for radio in radioList:
                theList += f'\n{str(radio)}'
            await message.channel.send(theList)
            return

        if isinstance(args, list) and len(args) == 1: # pause resume or stop (actions while playing)
            # extract action
            action = args[0]

            # what you can do before all of this is display the list
            if action == 'list':
                await self.cmd_radio(bot, message, command, [])
                return

            # get player
            player = self.get_player(message.guild)

            # do action
            if action == 'playing':
                msg = "La radio n'est pas jouée actuellement"

                radio_name = player.radio_name()
                channel_name = player.channel_name()
                if radio_name:
                    if player.is_paused():
                        msg = f'La radio { radio_name } est pausée dans le salon { channel_name }'
                    else:
                        msg = f'La radio { radio_name } est jouée dans le salon { channel_name }'
                
                await message.channel.send(
                    embed=discord.Embed(
                    title="État de la radio",
                        color=CONFIRM_COLOR,
                        description=msg,
                    )
                )
                return

            # stop if not in channel with bot

            # if user not in voice channel
            if not message.author.voice:
                return

            # if bot not in voice channel
            if not message.guild.voice_client:
                return
            
            # if bot not in same voice channel
            if message.guild.voice_client.channel != message.author.voice.channel:
                return
            
            if action == 'pause':
                player.pause()
            elif action == 'resume':
                player.resume()
            elif action == 'stop':
                await player.stop()
            
            #exit da fuck outa here
            return

        if isinstance(args, list) and len(args) == 2:
            if args[0] == 'play': # play a radio
                # get radio alias
                alias = str(args[1])

                # search for radio
                radio_desc = self.find_radio(alias)

                if not isinstance(radio_desc, RadioDescription):
                    await message.channel.send(
                        embed=discord.Embed(
                            title="Nom de radio incorrect",
                            color=ERROR_COLOR,
                            description= f"{ message.author.mention }, impossible de trouver la radio {alias}"
                        )
                    )
                    await self.cmd_radio(bot, message, command, [])
                    return

                # exit if user not in voice channel
                if not message.author.voice:
                    error = await message.channel.send(
                        embed=discord.Embed(
                            color=ERROR_COLOR,
                            description=message.author.mention + ", tu n'es pas dans un channel audio.",
                        )
                    )
                    await asyncio.sleep(2)
                    await error.delete()
                    return

                # get player
                player = self.get_player(message.guild)

                # go to voice channel
                await player.go_to(message.author.voice.channel)

                # play radio
                await player.play(radio_desc)

                await message.channel.send(embed=discord.Embed(title="Radio", color=CONFIRM_COLOR, description=f'Démarrage de ${player.radio.display_name} dans ${ player.channel_name() }...'))
            elif args[0] == "volume":
                # get player
                player = self.get_player(message.guild)

                changed = player.setVolume(args[1])

                if not changed:
                    error = await message.channel.send(
                        embed=discord.Embed(
                            color=ERROR_COLOR,
                            description="Impossible de lire la valeur du volume, merci de choisir un réel entre 0 et 100 inclus",
                        )
                    )
                    await asyncio.sleep(2)
                    await error.delete()
                    return

                await message.channel.send(embed=discord.Embed(title="Radio", color=CONFIRM_COLOR, description=f':speaker: Changement du volume de la radio à { player.volume } %'))
    
    async def update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        # check if not joined
        if before.channel is None:
            return

        # check if multiple persons after or if if no one now
        if len(before.channel.members) > 1 or len(before.channel.members) == 0:
            return

        # check if the only member left in channel is the bot :,(
        if before.channel.members[0] != before.channel.guild.me:
            return

        # check if player in guild
        player = None
        i = 0
        while i < len(self.players) and player is None:
            if self.players[i].guild == before.channel.guild:
                player = self.players[i]
            
            i += 1
        
        if player is None:
            return
            
        print("Radio player auto disconnecting from " + before.channel.name + " because empty room...")
        await player.stop()