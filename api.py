from aiohttp import web
from discord.ext import commands, tasks
import discord
import os
import aiohttp

app = web.Application()
routes = web.RouteTableDef()


def setup(bot):
    bot.add_cog(Webserver(bot))

class Webserver(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.web_server.start()

        @routes.get('/')
        async def welcome(request):
            return web.Response(text="Hello, world")

        @routes.get('/status/server/{serverId}')
        async def get_server_status(request):
            try:
                guild = await self.bot.fetch_guild(request.match_info['serverId'])
                res = []
                async for member in guild.fetch_members(limit=None):
                    try:
                        res.append(await self.get_user(member.id))
                    except:
                        pass
                return web.json_response( data=res, status=200)
            except Exception as e:
                print(e)
                return web.Response("Hmmm somethin went wronh", 500)

        @routes.get('/status/user/{name}')
        async def get_user_status(request):
            try:
                res = self.get_user(request.match_info['name'])
                return web.json_response( data=res, status=200)
            except Exception as e:
                print(e)
                return web.Response("Hmmm somethin went wronh", 500)

        self.webserver_port = os.environ.get('API_PORT', 5000)
        app.add_routes(routes)

    @tasks.loop()
    async def web_server(self):
        return

    @web_server.before_loop
    async def web_server_before_loop(self):
        await self.bot.wait_until_ready()
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host='0.0.0.0', port=self.webserver_port)
        await site.start()

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
            raise e

        return result
    
    async def get_user(self, id):
        user = await self.fetch_member(id)
        activities = []
        print(user.activities)
        for i in range(len(user.activities)):
            activity = user.activities[i]
            activities.append({
                'name': activity.name,
                'small_image': activity.small_image_url,
                'large_image': activity.large_image_url,
                'type': activity.type
            })
        
        res = {
            'avatar_url': str(user.avatar_url),
            'name': user.name,
            'status': str(user.status),
            'voice': user.voice is not None and user.voice.channel is not None,
            'activities': activities
        }
        if res['voice']:
            res['voice_channel'] = user.voice.channel.name if user.voice.channel is not None else None
        return res