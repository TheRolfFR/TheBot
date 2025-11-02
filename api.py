import os
from collections.abc import Mapping

from aiohttp import web
from discord.ext import commands, tasks
import discord

class Webserver(commands.Cog):
    def __init__(self, bot: commands.Bot, host=os.environ.get("API_PORT", "0.0.0.0") , port=os.environ.get("API_PORT", 5000)):
        self.bot = bot
        self.web_server_host = host
        self.webserver_port = int(port)
        self.password = os.environ.get("API_PASSWORD", "secret_password")  # DONT LEAVE THAT empty

        routes = web.RouteTableDef()

        @routes.get("/hello")
        async def welcome(request: web.Request):
            return web.Response(text="Hello, world")

        # @routes.get("/status/server/{serverId}")
        async def get_server_status(request: web.Request):
            try:
                guild = await self.bot.fetch_guild(request.match_info["serverId"])
                res = []
                async for member in guild.fetch_members(limit=None):
                    try:
                        res.append(await self.get_user(member.id))
                    except:
                        pass
                return web.json_response(data=res, status=200)
            except Exception as e:
                print(e)
                return web.Response("Hmmm somethin went wronh", 500)

        # @routes.get("/status/user/{name}")
        async def get_user_status(request: web.Request):
            try:
                res = self.get_user(request.match_info["name"])
                return web.json_response(data=res, status=200)
            except Exception as e:
                print(e)
                return web.Response("Hmmm somethin went wronh", 500)

        @routes.post("/send/embed/{user_id}/{password}")
        async def send_raw_embed(request: web.Request):
            input_password = request.match_info.get("password")
            if self.password != input_password:
                return web.Response(status=404)

            user_id = request.match_info["user_id"]
            user = await self.fetch_member(user_id)
            payload: Mapping[str, any] = await request.json()
            
            text = payload["username"]
            embeds = [discord.Embed.from_dict(e) for e in payload["embeds"]]

            await user.send(text, embeds=embeds)

            return web.Response(status=200)

        self.app = web.Application()
        self.app.add_routes(routes)

    async def cog_load(self) -> None:
        runner = web.AppRunner(self.app)

        await runner.setup()
        site = web.TCPSite(runner, host=self.web_server_host, port=self.webserver_port)
        await site.start()

        print(f"🌍 API running at {site._host}:{site._port}")

        return await super().cog_load()

    async def fetch_member(self, id):
        error = None
        result = None
        guilds = self.bot.guilds
        i = 0
        while result is None and i < len(guilds):
            guild = guilds[i]
            try:
                result = await guild.fetch_member(id)
            except Exception as e:
                error = e
            i += 1

        if result is None:
            raise error

        return result

    async def get_user(self, id):
        user = await self.fetch_member(id)
        activities = []
        print(user.activities)
        for i in range(len(user.activities)):
            activity = user.activities[i]
            activities.append(
                {
                    "name": activity.name,
                    "small_image": activity.small_image_url,
                    "large_image": activity.large_image_url,
                    "type": activity.type,
                }
            )

        res = {
            "avatar_url": str(user.avatar_url),
            "name": user.name,
            "status": str(user.status),
            "voice": user.voice is not None and user.voice.channel is not None,
            "activities": activities,
        }
        if res["voice"]:
            res["voice_channel"] = (
                user.voice.channel.name if user.voice.channel is not None else None
            )
        return res

async def setup(bot: commands.Bot):
    await bot.add_cog(Webserver(bot))
