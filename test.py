import asyncio

# Mocking the necessary parts of the original Sus class for testing
class MockGuild:
    def __init__(self, id):
        self.id = id

class MockMember:
    def __init__(self, id):
        self.id = id

class MockSus:
    def __init__(self):
        self.banned_users = {}  # {user_id: {guild_id: reason}}

    async def global_ban_user(self, user_id, guild_id, reason):
        if user_id not in self.banned_users:
            self.banned_users[user_id] = {}
        self.banned_users[user_id][guild_id] = reason

    async def ban_user(self, user_id, guild_id, reason):
        print(f"Banning user {user_id} from guild {guild_id} for reason: {reason}")
        await self.global_ban_user(user_id, guild_id, reason)

    def check_ban_reasons(self, user_id):
        if user_id in self.banned_users:
            reasons = self.banned_users[user_id]
            for guild_id, reason in reasons.items():
                print(f"User  {user_id} is banned from guild {guild_id} for reason: {reason}")
        else:
            print(f"User  {user_id} is not banned from any guilds.")

# Test function
async def test_ban_user():
    sus = MockSus()

    # Simulating banning a user from multiple guilds
    user_id = 123456
    guild1 = MockGuild(1)
    guild2 = MockGuild(2)

    await sus.ban_user(user_id, guild1.id, "Spamming")
    await sus.ban_user(user_id, guild2.id, "Scamming")

    # Check the ban reasons for the user
    sus.check_ban_reasons(user_id)

# Run the test
# asyncio.run(test_ban_user())

def add_ban_to_db():
    import os, requests
    BASE_URL = "https://mksentinel.vercel.app"
    API_KEY =  os.environ.get('SENTINEL_SECRET')
    headers = {'X-API-Key': API_KEY}


    member_data = {
        'memberId': '1320481335349084252',
        'username': 'justinfletcher06',
        'displayName': 'Support Administrator',
        'serverId': '410537146672349205',
        'serverName': 'Axie Infinity',
        'capturedMessage': '',
        'reason': 'Fake Support'
    }

    try:

        response = requests.post(
            f'{BASE_URL}/ban',
            headers=headers,
            json=member_data
        )

        if response.status_code == 201:
            print(f"Successfully banned user {member_data['username']}")
            return response.json()
        else:
            print(f"Failed to create ban. Status code: {response.status_code}")
            print(f"Error: {response.json()}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        return None

data = add_ban_to_db()