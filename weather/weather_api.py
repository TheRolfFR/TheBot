import json
import subprocess
from discord.ext import commands
from aiohttp import web
import os
from pathlib import Path

class WeatherAPI:
    def __init__(self, bot: commands.Bot, host="0.0.0.0", port=8080):
        self.bot = bot
        self.host = host
        self.port = port

        self.app = web.Application()
        self.runner: web.AppRunner | None = None

        # Register routes
        self.app.add_routes([
            web.get("/graph", self.handle_graph),
            web.get("/forecast", self.handle_forecast),
        ])

    async def handle_graph(self, request: web.Request):
        url = request.query.get("url")
        if not url:
            return web.Response(status=400)
        response = self.run_bin("meteoblue_graph", url, "--output", "lol.png")
        return web.Response()

    async def handle_forecast(self, request):
        url = request.query.get("url")
        if not url:
            return web.Response(status=400)
        response = self.run_bin("meteoblue_api", url)
        json_string = response.stdout.decode("utf-8")
        if json_string:
            return web.json_response(json.loads(json_string))
        else:
            return web.Response(status=500, body=response.stderr.decode("utf-8").strip())

    async def start(self):
        if self.runner:  # Already running
            return
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        site = web.TCPSite(self.runner, self.host, self.port)
        await site.start()
        print(f"✅ WeatherAPI running at http://{self.host}:{self.port}")

    async def stop(self):
        if self.runner:
            await self.runner.cleanup()
            self.runner = None
            print("🛑 WeatherAPI stopped")

    @property
    def api_folder(self):
        return Path(__file__).parent

    def run_bin(self, bin, *args):
        bin_path = self.api_folder / f"{bin}"
        running = [str(bin_path), *args]
        return subprocess.run(running, capture_output=True)
