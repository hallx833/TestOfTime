from twitchio.ext import commands

from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.types import AuthScope
from twitchAPI.helper import first
import json
from asyncinit import asyncinit
import asyncio
import random
from datetime import datetime, timezone
import time

@asyncinit
class Bot(commands.Bot):
    async def __init__(self):
        with open('C:/Users/evan/Dev/TestOfTime/config.json') as f:
            self.config = json.load(f)

        await self.auth()

        self.active = False

        super().__init__(token=self.token, prefix='!', initial_channels=[self.config['streamer']])

    async def auth(self):
        self.twitch = await Twitch(self.config['client_id'], self.config['client_secret'])
        target_scope = [AuthScope.CHAT_READ, AuthScope.CHAT_EDIT, AuthScope.MODERATOR_READ_CHATTERS, AuthScope.MODERATOR_READ_FOLLOWERS, AuthScope.CHANNEL_MANAGE_PREDICTIONS]
        auth = UserAuthenticator(self.twitch, target_scope, force_verify=False)
        self.token, self.refresh_token = await auth.authenticate()
        print(self.token)
        await self.twitch.set_user_authentication(self.token, target_scope, self.refresh_token)

        streamer = await first(self.twitch.get_users(logins=self.config['streamer']))
        self.streamer_id = streamer.id
    
    async def event_ready(self):
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')

    @commands.command()
    async def tot(self, ctx: commands.Context):
        self.active = True
        chatters = await self.twitch.get_chatters(self.streamer_id, self.streamer_id)

        testee = random.choice(chatters.data)
        testee_res = await first(self.twitch.get_users(logins=testee.user_name))
        testee_id = testee_res.id

        followers = await self.twitch.get_channel_followers(self.config['streamer'], user_id=testee_id)
        not_following = False
        if not followers.data:
            follow_date = datetime.now(timezone.utc)
            not_following = True
        else:
            follow_date = followers.data[0].followed_at

        await ctx.send(f'Test of time started. Howw long has {testee.user_name} been following? Type !tot_enter YY/MM/DD to guess')
        self.entries = {}
        await asyncio.sleep(10)
        self.active = False
        
        # date_entries = {user: (date := self.parse_date(entry[1])) for user, entry in self.entries.items() if date}
        date_entries = {}
        for user, entry in self.entries.items():
            date = self.parse_date(entry)
            if date:
                date_entries[user] = date

        winner = self.find_winner(follow_date, date_entries)
        
        if not_following:
            date_message = f"{testee.user_name} isn't following"
        else:
            date_message = f'{testee.user_name} followed on {follow_date.strftime("%y/%m/%d")}'
        await ctx.send(f'{winner} wins! {date_message}')
    
    def find_winner(self, follow_date, date_entries):
        return min(
            date_entries,
            key=lambda d: 
                abs((date_entries.get(d) - follow_date).total_seconds()))

    def parse_date(self, entry):
        try:
            date = datetime.strptime(entry, '%y/%m/%d')
            date = date.replace(tzinfo=timezone.utc)
        except:
            return False
        return date

    @commands.command()
    async def tot_enter(self, ctx: commands.Context): 
        if not self.active:
            await ctx.send(f'No Test of Time active')
            return

        self.entries[ctx.author.name] = ctx.message.content.removeprefix('!tot_enter ')
        
loop = asyncio.get_event_loop()

def main():
    bot = loop.run_until_complete(Bot())
    bot.run()

main()