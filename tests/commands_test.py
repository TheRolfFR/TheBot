""""
General command test file
"""

import pytest
import discord
import discord.ext.test as dpytest # pyright: ignore[reportMissingImports]
from unittest.mock import patch, PropertyMock
from bot import UTBot
from settings import PREFIX, STATUS_COLOR

@pytest.mark.asyncio
async def test_prefix(bot):
    assert bot.prefix == PREFIX

@pytest.mark.asyncio
async def test_ping(bot):
    with patch.object(UTBot, "latency", new_callable=PropertyMock) as attr_mock:
        attr_mock.return_value = 420

        embed = discord.Embed(
            color=STATUS_COLOR,
            description="**Ma latence est de ``420000``ms** :ping_pong: ",
        )

        await dpytest.message(PREFIX+"ping")

        assert dpytest.verify().message().embed(embed)

