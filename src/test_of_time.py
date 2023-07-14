from twitchio.ext import commands

from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.types import AuthScope
from twitchAPI.helper import first


class Bot(commands.Bot):

    def __init__(self):
        # Initialise our Bot with our access token, prefix and a list of channels to join on boot...
        # prefix can be a callable, which returns a list of strings or a string...
        # initial_channels can also be a callable which returns a list of strings...
        

        
        # with open('../auth.txt') as f:
        #     token = f.readline().rstrip()
        import json
        # Opening JSON file
        with open('config.json') as f:
            self.config = json.load(f)
        
        self.token = self.config['token']
        self.refresh_token = self.config['refreshToken']
        #with open('../channel.txt') as f:
        #    channel = f.readline().rstrip()
        #self.channel = channel
        channel = self.config['channel']
        super().__init__(token=self.token, prefix='!', initial_channels=[channel])

    # async def auth(self, token, refresh_token):
    #     twitch = await Twitch('8k1ait256yqr6e6l9rv5e5giigfyiw', 'c1yulaw84hfsy0baa65t49e65l19az')

    #     target_scope = [AuthScope.BITS_READ]
    #     auth = UserAuthenticator(twitch, target_scope, force_verify=False)
    #     # add User authentication
    #     await twitch.set_user_authentication(token, target_scope, refresh_token)

    async def event_ready(self):
        
        # Notify us when everything is ready!
        # We are logged in and ready to chat and use commands...
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')

    @commands.command()
    async def tot(self, ctx: commands.Context):
        twitch = await Twitch(self.config['clientID'], self.config['secret'])

        target_scope = [AuthScope.BITS_READ]
        auth = UserAuthenticator(twitch, target_scope, force_verify=False)
        # add User authentication
        await twitch.set_user_authentication(self.token, target_scope, self.refresh_token)
        # Get all of the chatters
        streamer = await first(self.twitch.get_users(logins=self.channel))
        streamer_id = streamer.id

        chatters = self.twitch.get_chatters(streamer_id, streamer_id)

        print(chatters)

        # Pick a random chatter and get their follow date

        # Create a prediction

        # After some time resolve prediction

        await ctx.send(f'Hello {ctx.author.name}!')


bot = Bot()
bot.run()
# bot.run() is blocking and will stop execution of any below code here until stopped or closed.