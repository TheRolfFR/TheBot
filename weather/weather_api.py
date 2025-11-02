import json
import subprocess
from subprocess import PIPE
from discord.ext import commands
import aiofiles
from aiohttp import web
import os
from pathlib import Path
import sys
import tempfile
from typing import Tuple


class WeatherAPI:
    def __init__(self, bot: commands.Bot, host="0.0.0.0", port=8080):
        if bot is None:
            return

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
        darkmode = request.query.get("darkmode", "false") != "false"
        transparent = request.query.get("transparent", "false") != "false"

        temp_path, exit_code = self.create_temp_graph(url, darkmode, transparent)

        if exit_code != 0:
            return web.Response(status=500, text=f"Graph failed with exit code {exit_code}")
        
        try:
            async with aiofiles.open(temp_path, 'rb') as f:
                data = await f.read()
                self.remove_file(temp_path)
            return web.Response(body=data, content_type='image/png')
        except FileNotFoundError:
            return web.Response(status=404, text='Image not found')
        except Exception as e:
            return web.Response(status=500, text=f"Error: {str(e)}")

    def create_graph(self, url: str, output: str, darkmode: bool, transparent: bool) -> Tuple[str, int]:
        darkmode_value = "true" if darkmode else "false"
        transparent_value = "true" if transparent else "false"

        if not output.endswith(".png"):
            return "", -1

        exit_code = self.start_popen(
            "meteoblue_graph", url,
            "--output", output,
            "--darkmode", darkmode_value,
            "--transparent", transparent_value,
        )

        return output, exit_code

    def create_temp_graph(self, url: str, darkmode: bool, transparent: bool) -> Tuple[str, int]:
        temp_dir = Path(tempfile._get_default_tempdir())
        temp_name = next(tempfile._get_candidate_names())
        temp_path = str((temp_dir / temp_name).with_suffix(".png"))

        return self.create_graph(url, temp_path, darkmode, transparent)

    def remove_file(self, output: str):
        os.remove(output)

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
        print(f"🌤️ WeatherAPI running at http://{self.host}:{self.port} ✅")

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

    def start_popen(self, bin, *args):
        bin_path = self.api_folder / bin
        bin_with_args = [str(bin_path), *args]
        print(" ".join(bin_with_args))
        process = subprocess.Popen(
            bin_with_args,
            stdout=PIPE,
            stderr=PIPE,
            text=True
        )
        stdout_done = False
        while not stdout_done:
            line = process.stdout.readline() or process.stderr.readline()
            if line == '' and (process.poll() or process.returncode) is not None:
                stdout_done = True
            if line:
                print(line.strip())

        print(f"{bin_path} finished with code {process.returncode}")
        return int(process.returncode)
