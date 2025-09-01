import discord
import asyncio
import logging

from settings import CREATOR_ID

from weather.weather_api import WeatherAPI

weather_api = WeatherAPI(None)

async def cmd_meteoblue(
    bot: discord.Client, message: discord.Message, command: str, args
):
    """
    Show meteoblue graph image
    """
    url = args[0] if len(args) else "https://www.meteoblue.com/fr/meteo/semaine/grenoble_france_3014728"
    await message.add_reaction("⏳")
    graph_path, exit_code = weather_api.create_temp_graph(url, darkmode=True, transparent=False)
    await message.remove_reaction("⏳", bot.user)

    if exit_code != 0:
        await message.add_reaction("❌")
        await message.reply(f"Could not create graph, got exit code {exit_code}")
        return
    
    await message.add_reaction("✅")
    await message.reply(file=discord.File(graph_path), mention_author=False)
    weather_api.remove_file(graph_path)
    