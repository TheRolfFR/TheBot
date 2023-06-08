"""
pytest discord bot config
"""

import discord
from discord.ext import commands
import pytest_asyncio
import discord.ext.test as dpytest # pyright: ignore[reportMissingImports]

from settings import PREFIX

from bot import UTBot, get_command_map

@pytest_asyncio.fixture(scope="function")
async def bot():
    intents = discord.Intents.all()
    intents.members = True
    intents.message_content = True

    result = UTBot(PREFIX, intents=intents)
    for cmd_name, cmd_callback in get_command_map(False).items():
        result.add_command(commands.Command(cmd_callback, name=cmd_name))

    await result._async_setup_hook()  # setup the loop

    dpytest.configure(result)

    return result