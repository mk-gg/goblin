import requests

from selfcord.ext import commands
from src.utils import *

guilds = {
    438327036205858818: {
        'ban_channel': 1110939231469195274,
        'color': '#95BDFF'
    }, # test 
    1229357590295871529: {
        'ban_channel': 1229357928226754570,
        'color': '#8DDFCB'
    }, # test 2
    1229357703240089641: {
        'ban_channel': 1229358040168267838, 
        'color': '#EDB7ED'
    }, # test 3

    # 410537146672349205: {
    #     'ban_channel': 976324309981204542,
    #     'color': '#E8C872'
    # }, # Axie Infinity 
    # 930892666705694800: {
    #     'ban_channel': 1044659893803692184,
    #     'color': '#7FC7D9'
    # } # Ronin Network
}


def is_discord_url(url):
    parsed_url = urllib.parse.urlparse(str(url))  # Convert url to string
    domain = parsed_url.netloc
    return domain.endswith(("discord.com", "discord.gg"))

def get_guild_name(url):
    # Extract the invite code from the URL using a regular expression
    match = re.search(r'https?://discord(?:\.com/invite|\.gg)/([a-zA-Z0-9-]+)', url)
    if match:
        invite_code = match.group(1)
        try:
            response = requests.get(f"https://discord.com/api/v8/invites/{invite_code}") 
            response.raise_for_status()  # Raise an exception for a failed request

            data = response.json()


            if "guild" in data:
                guild_name = data["guild"]["name"]
                return guild_name
 
            
            
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except requests.exceptions.RequestException as err:
            print(f"Error occurred: {err}")
    else:
        print("Invalid Discord invite link")

class Sus(commands.Cog):
    def __init__(self, client):
        self.client = client

        self.main_queue = asyncio.Queue()
        self.banned_users = {}
        self.user_locks = {}
        self.background_task = asyncio.create_task(self.process_queue())

    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        """
        Listen for user updates and add them to the main queue.

        Args:
            before (discord.User): The user object before the update.
            after (discord.User): The user object after the update.
        """

        # Get the list of guilds that this cog is monitoring
        my_guilds = [guild for guild in self.client.guilds if guild.id in guilds]
        # Iterate through the guilds and check if the updated user is a member
        for guild in my_guilds:
            member = guild.get_member(before.id)
            if member is not None:
                # If the user is a member, add their update to the main queue
                data = {
                    'user_id': after.id,
                    'guild': guild,
                    'member': after,
                    'message': None,
                    'event': 'update'
                }
                await self.main_queue.put(data)
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        """
        Listen for messages and add their data to the main queue.
        
        Args:
            member (discord.Member): The member has joined the server
        
        Returns:
            None
        """
        # Check if the message was sent in a guild that we're listening to
        if member.guild.id not in guilds:
            return
        # Create a dictionary of data to store about the newly joined member
        data = {
            'user_id': member.id,
            'guild': member.guild,
            'member': member,
            'message': None,
            'event': 'join'
        }
        # Add the message data to the main queue
        await self.main_queue.put(data)

    @commands.Cog.listener()
    async def on_message(self, message):
        """
        Listen for messages and add their data to the main queue.
        
        Args:
            message (discord.Message): The message that was sent.
        
        Returns:
            None
        """
        # Check if the message was sent in a guild that we're listening to
        if message.guild.id not in guilds:
            return
        # Check if the message author is within 45 day after joining the server
        try:
            is_within_date = check_date(message.author.joined_at.strftime("%Y-%m-%d %H:%M:%S%z"), 45)
        except Exception as e:
            print(f"On_message error: {e}")

        if is_within_date:
            # Create a dictionary of data to store about the message
            data = {
                    'user_id': message.author.id,
                    'guild': message.guild,
                    'member': message.author,
                    'message': message,
                    'event': 'message'
                }
            # Add the message data to the main queue
            await self.main_queue.put(data)

    async def process_queue(self):
        while True:
            data = await self.main_queue.get()

            user_id = data['user_id']
            data_guild_id = data['guild'].id

            guild_obj = data["guild"]
            color = guilds[guild_obj.id]['color']

            time_format = f"[{get_time_now()}]"
            guild_format = f"[[{color}]{guild_obj}[/]]"


            async with self.user_locks.setdefault(user_id, asyncio.Lock()):

                if user_id in self.banned_users:
                    banned_servers = list(self.banned_users[user_id])

                    if data_guild_id in banned_servers:
                        print(f"{time_format} {guild_format} User: {user_id} is already banned from the current server!")
                    elif data_guild_id in guilds:
                        print(f"{time_format} {guild_format} User: {user_id} is banned from the ff. server(s): {banned_servers}")
                        # Since a user is detected from a banned server, attempt to ban

                        await self.global_ban_user(user_id, data_guild_id) # Add the user with guild id to the banned list
                        
                        print(f"{time_format} {guild_format} Banning user: {data_guild_id}")
                        await self.ban_user(data, "Flagged!")

                else:

                    print(f"{time_format} {guild_format} Data received from: {user_id}")

                    event_handlers = {
                        'message': lambda: print(f"{time_format} {guild_format} {data['member'].name} sent a message  ({user_id})"),
                        'update': lambda: print(f"{time_format} {guild_format} {data['member'].name} updated its profile  ({user_id})"),
                        'join': lambda: print(f"{time_format} {guild_format} {data['member'].name} just joined  ({user_id})"),
                    }

                    if data['event'] == 'message':
                        # Process message data
                        extract_url = extract_urls(data['message'].content)
                        if not extract_url:
                            print("No extracted url")
                        else:
                            final_url = get_final_url(extract_url[0])

                            if final_url:
                                if is_discord_url(final_url):
                                    guild_name = get_guild_name(final_url)
                                    if guild_name:
                                        print(f"Guild name: {guild_name}")
                                         
                                    create_panel(final_url, "Discord Url", guild_obj.name,  data['message'])    

                    #elif data['event'] == 'update' or data['event'] == 'join':

                        

            self.main_queue.task_done()



async def setup(client):
    await client.add_cog(Sus(client))