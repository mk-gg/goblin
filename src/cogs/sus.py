import requests

from selfcord.ext import commands
from src.utils import *

from datetime import datetime, timedelta, timezone

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

    410537146672349205: {
        'ban_channel': 976324309981204542,
        'color': '#E8C872'
    }, # Axie Infinity 
    930892666705694800: {
        'ban_channel': 1044659893803692184,
        'color': '#7FC7D9'
    } # Ronin Network
}

server_bots = {
    396548639641567232,  # Mavis Market Bot (new)
    1110593454012104745, # Mavis Market Bot
    823695836319055883,  # AxieBot 
    1230221894221824222, # Axie.Bot [App]
    1217477415757025444, # EndlessHerald [Axie Infinity]

}

flagged_names = [

    'ᎠᎡΟР',
    'ᎠᎡОР',
    'ᎠᎡΟΡ',
    'ᎠᎡΟᏢ',
    'ᎠᎡОΡ',
    

    'ᎠᎡОᏢ',
    'ᎠᎡΟᏢՏ',
    'ᎠᎡΟΡՏ',
    'ᎠᎡΟРՏ',
    'ᎠᎡОΡЅ',
    'zkЅуոс',
    'ᏟᏞΑІΜΙΝᏀ',
    'ᏟᏞΑӀМӏΝᏀ',
    'СᏞΑӀМӏΝᏀ',
    'СᏞΑӀΜІΝᏀ',
    'ᏟᏞΑІМІΝᏀ',
    'ᏟᏞΑІМӀΝᏀ',
    'ᏟᏞΑӏΜ',
    'ᏟᏞΑӏΜΙΝᏀ',
    'CHECK BIO',
    'ᏟНΕᏟΚ ΒІΟ',
    'GOTO BIO',
    'ᏀΟТΟ ΒӀО',
    'ᏀΟΤΟ ΒΙО',
    'ᏀОТΟ ΒІО',
    'ᏀΟΤΟ ΒӀО',
    'ᏀОТΟ ВӏΟ',
    'ᏀОΤΟ ΒӏΟ',
    'ᏀОТΟ ВІΟ',
    'LOOK BIO',
    'ᏞΟОᏦ ВΙΟ',
    'ᏞΟОᏦ ВІΟ',
    'ᏞΟΟΚ ΒӀО',
    'ᏞΟΟᏦ ВІΟ',
    'ᏞООᏦ ВӏΟ',
    'ᏞОΟᏦ ВӏО',
    'ᏞОΟᏦ ВΙΟ',
    'SEE BIO',
    'ՏΕЕ ВӏΟ',
    'ՏЕΕ ΒӏΟ',
    'ՏΕΕ ΒӏΟ',
    'ЅЕЕ ΒІО',
    'ЅΕΕ ВІΟ',
    'ЅΕЕ ВӀО',
    'ЅЕΕ ВІО',
    'ՏΕΕ ВӀО',
    'ЅΕЕ ВІΟ',
    'ՏЕЕ ΒӏО',
    'ՏЕΕ ΒΙО',
    'ЅЕΕ ВӀΟ',
    'ЅΕΕ ΒӀО',
    'ЅΕΕ ΒΙΟ',
    'ՏЕЕ ВӏΟ',
    'ЅΕΕ ΒІΟ',
    'ЅЕΕ ВӏО',
    'READ BIO',
    'ᎡΕΑᎠ ВΙΟ',
    'ᎡЕΑᎠ ВӀО',
    'ᎡΕΑᎠ ΒІΟ',
    'ᎡΕΑᎠ ВӏО',
    'ᎡΕΑᎠ ВΙО',
    'ᎡΕΑᎠ ВӏО',
    'ᎡΕΑᎠ ΒӀΟ',
    'ᎡΕΑᎠ ВӀΟ',
    'ᎡЕΑᎠ ΒӀО',
    'ᏟΗΕᏟΚ ΒІО',
    'СΗЕСΚ ВΙΟ',
    'ᏟΗΕᏟΚ ВӀО',
    'Ꭱеԝаrⅾ Ρrоցrаⅿ',
    '𝐁𝐈𝟎',
    'ᏞӀᏙΕ', 
    'ᏞӀᏙЕ',
    'ᏞΙᏙЕ',
    'ᏞΙᏙΕ',
    'ᏞІᏙΕ',
    'ᏞІᏙЕ',
    'ᎠΕᏞІᏙΕᎡ',
    'ᎠΕᏞӏᏙЕᎡ',
    'ᎠЕᏞІᏙЕᎡ',
    'ᎠЕᏞӏᏙЕᎡ',
    'ᎠΕᏞІᏙЕᎡ',
    'ᎠЕᏞΙᏙΕᎡ',
    'DELIVER',
    'ᎠΕᏞӀᏙΕᎡ',
    'ᎠЕᏞΙᏙЕᎡ',
    'ᎠЕᏞІᏙЕᎡΥ',
    'ᎠЕᏞΙᏙЕᎡΥ',
    'ᎠΕᏞΙᏙΕᎡ',

    'ᎠΕᏞΙᏙЕᎡ',
    'AIRDROPPING',
    'ΑӏᎡᎠᎡОᏢΡӀΝᏀ',
 
    


   

    'ᏞӏᏙΕ',
    'Βrіⅾցе',
    'Вrіⅾցе',
    
    



    'ANNOUNCEMENT',
    '📢ANOUNCEMENT',
    '📢ANNOUNCEMENTS',
    '📢ANNOUNCEMENT',
    '📡 ANNOUNCEMENT',
    '📢 Annoucement',
    'HELPLINE✪',

 

    's33.b1()',   

    'announcements',
    'tether_survey',
    'tether_drop',
    'tether_reward',
    'tether_questionnaire',
    'tether_study',
    'tether_poll',
    'tether_official',
    'tether_prompt',
    'tether_claim',

    'tethersurvey',
    'tetherdrop',
    'tetherreward',
    'tetherquestionnaire',
    'tetherstudy',
    'tetherpoll',
    'tetherofficial',
    'tetherprompt',
    'tetherclaim',

    'usdt_prompt',
    'usdt_study',
    'usdt_drop',
    'usdt_claim',
    'usdt_official',
    'usdt_poll',
    'usdt_survey',
    'usdt_reward',
    'usdt_questionnaire',

    'usdt_prompt',
    'usdtstudy',
    'usdtdrop',
    'usdtclaim',
    'usdtprompt',
    'usdtofficial',
    'usdtpoll',
    'usdtsurvey',
    'usdtreward',
    'usdtquestionnaire',

    'injectiveclaim',
    'huobiclaim',   
    
    'autobot',
    'autoinfo',  
    'alertbot',
    'alertinfo', 
    'alertmessage', 
    'automessage', 
    'claimbot', 
    'claiminfo', 
    'claimmessage',
    'instantbot',
    'instantinfo', 
    'instantmessage',
    'notifybot',
    'notifyinfo',
    'notifymessage'
]

def is_scam_server(name):
    if name is None:
        return False
    scam_keywords = {"support", "tickets","support-tickets", "support server", "ticket support", "helpdesk center", "create ticket", "helpdesk", "help desk", "help center", "support ticket", "ticket tool", "ticket", "server support", "customer support", "technical support", "help-center", "help", "help-centre"}
    return any(keyword.lower() in name.lower() for keyword in scam_keywords)

def is_nsfw_server(name):
    if name is None:
        return False
    nsfw_keywords = {"NSFW", "Teen", "Onlyfan", "Onlyfans", "Leaks", "Nude", "Sex", "Tiktok", "SexCam", "Slut", "Porn", "18+", "hentai"}
    return any(keyword.lower() in name.lower() for keyword in nsfw_keywords)

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


    

def get_differences(before, after):
    common_attributes = set(dir(before)) & set(dir(after))
    differences = {}

    for attr in common_attributes:
        if hasattr(before, attr) and hasattr(after, attr):
            if attr in ['note', 'avatar_decoration', '_avatar_decoration', 'avatar', 'display_avatar']:  # Add attributes to exclude here
                continue
            val1 = getattr(before, attr)
            val2 = getattr(after, attr)
            if not callable(val1) and not callable(val2):
                try:
                    if val1!= val2:
                        key = f"{val1} -> {val2}"
                        if key not in differences:
                            differences[key] = []
                        differences[key].append(attr)
                except Exception as e:
                    pass

    if differences:
        for key, attrs in differences.items():
            try:
                print(f"  {', '.join(attrs)}: {key}")
            except Exception as e:
                pass

class Sus(commands.Cog):
    def __init__(self, client):
        self.client = client

        self.main_queue = asyncio.Queue()
        self.banned_users = {}
        self.user_locks = {}
        self.background_task = asyncio.create_task(self.process_queue())
    


    async def is_blacklisted_name(self, data):
        """
        Checks data's attribute (name, display_name & global_name)
        if it's similar to flagged_names

        return boolean
        """

        names = [data.name, data.display_name, data.global_name]
        names = [name for name in names if name is not None]
        regex = "|".join(flagged_names)
        is_blacklisted = bool(re.search(regex, "|".join(names)))
        return is_blacklisted
    async def mutual_guild(self, guild, member_id):
        """
        Check if a user is in the same server as the bot.

        Args:
            guild (discord.Guild): The guild object to check for the user.
            member_id (int): The ID of the user to check.

        Returns:
            bool: True if the user is in the same server as the bot, False otherwise.

        Raises:
            discord.errors.NotFound: If the user is not found in the guild.
        """
        try:
            resp = await guild.fetch_member(member_id)
            return True
        except selfcord.errors.NotFound:
            return False
        
    async def timeout_user(self, data, reason):
        if not await self.mutual_guild(data['guild'], data['member'].id):
            print(f"Timeout User (Member not found in guild): {data['member'].id}")
            return

        guild = data['guild']
        member = data['member']

        try:
            await member.timeout(timedelta(seconds=60), reason=reason)
        except Exception as e:
            print(f"Error timing out member: {e}")
            return

        color_guild = guilds[guild.id]['color']
        event_msg = f"[#7e8329]Timeout[/]"
        time_format = f"[{get_time_now()}]"
        guild_format = f"[[{color_guild}]{guild}[/]]"

        print(f"{time_format} {guild_format} {event_msg} {member.id} - {member}   {reason}")
        

    async def kick_user(self, data, reason):
        is_user_present = await self.mutual_guild(data['guild'], data['member'].id)
        if is_user_present:
            try:
                guild = data['guild']
                #user = guild.fetch_member(data['member'].id)
            except selfcord.NotFound as e:
                print(f"Kick User (Failed to fetch member): {e}")

            
   
            dguild_id = data['guild'].id
            color_guild = guilds[dguild_id]['color']

            event_msg = f"[#b98542]KICK[/]"
            time_format = f"[{get_time_now()}]"
            guild_format = f"[[{color_guild}]{data['guild']}[/]]"


            print(f"{time_format} {guild_format} [{event_msg}] {data['member'].id} - {data['member']}   {reason}")

            channel = guild.get_channel_or_thread(guilds[guild.id]['ban_channel'])
            await channel.send(f"<@{data['member'].id}>")

            

 
            await guild.kick(data['member'], reason=reason)
            await channel.send(
                f'**Kicked**\n'
                f'UID: {data["member"].id}\n'
                f'Reason: {reason}'
            )


    async def ban_user(self, data, reason, delete_message_seconds=0):
        is_user_present = await self.mutual_guild(data['guild'], data['member'].id)
        if is_user_present:
            try:
                guild = data['guild']
                #user = guild.fetch_member(data['member'].id)
            except selfcord.NotFound as e:
                print(f"Ban User (Failed to fetch member): {e}")

            
   
            dguild_id = data['guild'].id
            color = guilds[dguild_id]['color']

            event_msg = f"[#f595ad]BAN[/]"
            time_format = f"[{get_time_now()}]"
            guild_format = f"[[{color}]{data['guild']}[/]]"


            print(f"{time_format} {guild_format} [{event_msg}] {data['member'].id} - {data['member']}   {reason}")

            channel = guild.get_channel_or_thread(guilds[guild.id]['ban_channel'])
            await channel.send(f"<@{data['member'].id}>")

            if delete_message_seconds > 0:
                await asyncio.sleep(uniform(4, 8))

 
            await guild.ban(data['member'], reason=reason, delete_message_seconds=delete_message_seconds)
            await channel.send(
                f'**Banned**\n'
                f'UID: {data["member"].id}\n'
                f'Reason: {reason}'
            )

    async def global_ban_user(self, user_id, guild_id):
        if user_id not in self.banned_users:
            self.banned_users[user_id] = set()
        self.banned_users[user_id].add(guild_id)

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
                #get_differences(before, after)
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
        
        is_within_date = False
        # Check if the message author is within 45 day after joining the server
        try:
            is_within_date = check_date(message.author.joined_at.strftime("%Y-%m-%d %H:%M:%S%z"), 45)
        except Exception as e:
            pass
            
        if is_within_date:

            if message.type == selfcord.MessageType.auto_moderation_action:
                for embed in message.embeds:
                    embed_dict = embed.to_dict()
                    sent_message = embed_dict.get('description', '')
            else:
                sent_message = message.content
            # Create a dictionary of data to store about the message
            data = {
                    'user_id': message.author.id,
                    'guild': message.guild,
                    'member': message.author,
                    'message': sent_message,
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

                if user_id in server_bots:
                    continue

                if user_id in self.banned_users:
                    banned_servers = list(self.banned_users[user_id])

                    if data_guild_id in banned_servers:
                        print(f"{time_format} {guild_format} User: {user_id} is already banned from the current server!")
                    elif data_guild_id in guilds:
                        print(f"{time_format} {guild_format} User: {user_id} is banned from the ff. server(s): {banned_servers}")
                        # Since a user is detected from a banned server, attempt to ban

                        await self.global_ban_user(user_id, data_guild_id) # Add the user with guild id to the banned list
                        print(f"{time_format} {guild_format} Banning user: {data_guild_id}")
                        await self.ban_user(data, "Scam Bio Link")

                else:

                    # print(f"{time_format} {guild_format} Data received from: {user_id}")

                    event_handlers = {
                        'message': lambda: print(f"{time_format} {guild_format} [MESSAGE] {data['member'].name}: {data['message']}   ({user_id})"),
                        'update': lambda: print(f"{time_format} {guild_format} [UPDATE] {data['member'].name} | {data['member'].display_name} ({user_id})"),
                        'join': lambda: print(f"{time_format} {guild_format} [JOIN] {data['member'].name} | {data['member'].display_name}  ({user_id})"),
                    }

                    if data['event'] in event_handlers:
                        event_handlers[data['event']]()

                    

                    # Process message data
                    if data['event'] == 'message':
                        detected_url = scan_message_url(data['message'])
                        if detected_url:
                            if is_discord_url(detected_url):
                                guild_name = get_guild_name(detected_url)
                                if guild_name:
                                    
                                    if is_scam_server(guild_name):
                                        create_panel(detected_url, "Scam Server", guild_name,  data['message'], data['member'])
                                        
                                        await self.global_ban_user(user_id, data_guild_id)
                                        print(f"{time_format} {guild_format} [#f595ad]Banning user[/] {data['user_id']}")
                                        await self.ban_user(data, "Scam Attempt", 3000)
                                    
                                    if is_nsfw_server(guild_name):
                                        create_panel(detected_url, "NSFW Server", guild_name,  data['message'], data['member'])
                                        await self.timeout_user(data, "NSFW Spam / Hacked Account")
                                        await self.kick_user(data, "NSFW Spam / Hacked Account")
                                         
                                        
                    
                    if data['event'] == 'update' or data['event'] == 'join':
                        
                        is_flagged = await self.is_blacklisted_name(data['member'])

                        if is_flagged:
                            print(f"{time_format} {guild_format} [#f595ad]Flagged Name![/] - {data['user_id']}")
                            await self.global_ban_user(user_id, data_guild_id)
                            await self.ban_user(data, "Scam Bio Link")



                        

            self.main_queue.task_done()



async def setup(client):
    await client.add_cog(Sus(client))
