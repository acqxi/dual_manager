import os

import discord
from discord.ext import commands

from keep_alive import keep_alive

#from dotenv import load_dotenv
#load_dotenv()

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(
    command_prefix="d!",  # Change to desired prefix
    case_insensitive=True,  # Commands aren't case-sensitive
    intents=intents  # Due to an API change Discord is now forcing developers who want member caching to explicitly opt-in to it
)

bot.author_id = 402394522824474624  # Change to your discord id!!!


@bot.event
async def on_ready():  # When the bot is ready
    print( "I'm in" )
    print( bot.user )  # Prints the bot's username and identifier


extensions = [
    'cogs.bot_dev_setting',  # Same name as it would be if you were importing it
    #'xps.major',
    'react.major',
    'react.set',
    'cogs.game',
    #'xp_main',
    'game.3t',
]

if __name__ == '__main__':  # Ensures this is the file being ran
    for extension in extensions:
        bot.load_extension( extension )  # Loades every extension.

keep_alive()  # Starts a webserver to be pinged.
token = os.getenv( "DISCORD_BOT_SECRET" )
bot.run( token )  # Starts the bot
