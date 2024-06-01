from selfcord.ext import commands
from src.utils import *
class Sus(commands.Cog):
    def __init__(self, client):
        self.client = client

async def setup(client):
    await client.add_cog(Sus(client))