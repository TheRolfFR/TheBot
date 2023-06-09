"""
pytest discord bot config
"""

import asyncio
import discord
import pytest
from discord.ext import commands
from discord.ext.commands import Context
import pytest_asyncio
import discord.ext.test as dpytest # pyright: ignore[reportMissingImports]
from settings import PREFIX

from bot import UTBot, get_command_map, CommandCallback

@pytest.fixture(scope="session")
def event_loop():
    return asyncio.get_event_loop()

def ctx_to_callback(func: CommandCallback):
    async def inner(ctx: Context):
        splitted = ctx.message.content[len(ctx.bot.prefix) :].split(" ")
        message = ctx.message
        command = splitted[0]
        args = splitted[1:]
        bot = ctx.bot
        await func(bot, message, command, args)

    return inner

@pytest_asyncio.fixture(scope="session", autouse=True)
async def bot():
    intents = discord.Intents.all()
    intents.members = True
    intents.message_content = True

    result = UTBot(PREFIX, intents=intents)
    for cmd_name, cmd_callback in get_command_map(False).items():
        result.add_command(commands.Command(ctx_to_callback(cmd_callback), name=cmd_name))

    # setup the loop
    await result._async_setup_hook()  # pyright: ignore[reportMissingImports]

    dpytest.configure(result)

    print("bot", "ready")

    return result