# goblin

<p align="center">
  

  <img src="https://i.imgur.com/FNIK8ds.gif" alt="Preview" />

 
</p>

A Discord bot designed to detect and prevent malicious activity in your server.



## Features
- Anti homoglyph attack
- Bot detection
- URL scanning
- Handles multiple server
- Cog System

# Usage
1. Install the required dependencies
```sh
pip install -r requirements.txt
pip install git+https://github.com/dolfies/discord.py-self@renamed#egg=selfcord.py
```
2. Get your discord token.
```json
{
    "token": "your token here!",
    "prefix": ".",
    "apikeys": {}
}
```
3. Replace the guild and channel id in sus.py with your preferred id.
```sh
guilds = {
    your_guild_id: {
        'ban_channel': your_channel_id,
        'color': '#95BDFF'
    },  
    your_guild_id_2: {
        'ban_channel': your_channel_id_2,
        'color': '#8DDFCB'
    }
}
```
4. After editing, save it and run the bot.
```sh
python main.py
```
