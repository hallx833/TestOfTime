from twitchio.ext import commands

from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.types import AuthScope
from twitchAPI.helper import first
import json


class Bot(commands.Bot):

    def __init__(self):
        with open('config.json') as f:
            self.config = json.load(f)

        self.auth()

        super().__init__(token=self.token, prefix='!', initial_channels=[self.config['streamer']])

    async def auth(self):
        self.twitch = await Twitch(self.config['client_id'], self.config['client_secret'])
        target_scope = [AuthScope.MODERATOR_READ_CHATTERS, AuthScope.MODERATOR_READ_FOLLOWERS, AuthScope.CHANNEL_MANAGE_PREDICTIONS]
        auth = UserAuthenticator(self.twitch, target_scope, force_verify=False)
        self.token, self.refresh_token = await auth.authenticate()
        await self.twitch.set_user_authentication(self.token, target_scope, self.refresh_token)

        streamer = await first(self.twitch.get_users(logins=self.config['streamer']))
        self.streamer_id = streamer.id

    async def event_ready(self):
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')

    @commands.command()
    async def tot(self, ctx: commands.Context):
        chatters = await self.twitch.get_chatters(self.streamer_id, self.streamer_id)
        await ctx.send(f'Hello {chatters.data}!')


bot = Bot()
bot.run()