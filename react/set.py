import os
import sqlite3

import discord
from discord.ext import commands
from discord.ext.commands import context
from discord.ext.commands.core import has_permissions
from discord.ext.commands.errors import DisabledCommand

from . import gReactVal

conn = sqlite3.connect( os.path.join( os.path.dirname( __file__ ) + '\\reaction.db' ) )
cursor = conn.cursor()
cursor.execute( "CREATE TABLE IF NOT EXISTS ind (guild integer, msg integer, emoji text, role integer, type text)" )
conn.commit()
conn.close()


def save_to_sqlite( table, *args ) -> str:
    args = [ f"'{s}'" for s in args ]
    conn = sqlite3.connect( os.path.join( os.path.dirname( __file__ ) + '\\reaction.db' ) )
    cursor = conn.cursor()
    if len( list( cursor.execute( f"SELECT * FROM {table} WHERE msg={args[1]} AND emoji={args[2]}" ) ) ):
        sql_exc = f"UPDATE {table} SET role={args[3]},type={args[4]} WHERE msg={args[1]} AND emoji={args[2]}"
    else:
        sql_exc = f"INSERT INTO {table} VALUES ( {','.join(args)} )"
    print( f"do : {sql_exc}" )
    cursor.execute( sql_exc )
    conn.commit()
    conn.close()
    return sql_exc


def get_react_list( type: str, guildID, msgID ) -> dict:
    if type == "ind":
        try:
            print( gReactVal.reactSetInd[ guildID ][ msgID ] )
            return gReactVal.reactSetInd[ guildID ][ msgID ]
        except KeyError:
            return None


def transGRL2S( di: dict ):
    s = '獨立關聯:\n'
    j = '單選關聯:\n'
    for key, item in di.items():
        s += f"{item[0].name}:{item[1].mention}\n" if item[ 2 ] else ''
        j += f"{item[0].name}:{item[1].mention}\n" if not item[ 2 ] else ''
    return s + j


class ReactionConfigSetting( commands.Cog ):
    '''user do setting with reaction configuration'''

    def __init__( self, bot: commands.Bot ):
        self.bot = bot

    async def cog_check( self, ctx: commands.Context ):
        '''
        The default check for this cog whenever a command is used. Returns True if the command is allowed.
        '''
        return ctx.guild.id in [ 690548499233636362, 741429518484635749, 777758608930766878, 847028111441920010 ]

    @staticmethod
    async def sentMsgBaseData( sent, guild: discord.Guild, msg: discord.Message ):
        short_content = f"[{msg.content}]" if len( msg.content ) < 12 else f"[{msg.content[:5]}...{msg.content[-5:]}"
        ind = '沒有關聯' if ( indC := get_react_list( 'ind', guild.id, msg.id ) ) is None else transGRL2S( indC )
        await sent( f"{short_content}:{msg.id}\n{ind}" )

    @commands.group( name="reaction_relationship", aliases=[ 'rr' ] )
    @has_permissions( administrator=True )
    async def reaction_relationship( self, ctx: commands.Context ):
        pass

    @reaction_relationship.command( name='search', aliases=[ 's' ] )
    async def search( self, ctx: commands.Context, msg: discord.Message ):
        await ReactionConfigSetting.sentMsgBaseData( ctx.send, ctx.guild, msg )

    @reaction_relationship.command( name='active', aliases=[ 'a' ] )
    async def active( self, ctx: commands.Context ):
        await gReactVal.activeFunction( ctx.send, ctx.guild )

    async def write_raw( self, ctx: commands.Context, msg: discord.Message, emoji: str, role: discord.Role, type: str ):
        try:
            emoji = discord.Emoji( emoji )
        except TypeError:
            emoji = gReactVal.DefaultEmoji( emoji )

        if ctx.guild.id not in list( gReactVal.reactSetInd.keys() ):
            gReactVal.reactSetInd[ ctx.guild.id ] = { msg.id: { str( emoji ): ( emoji, role, type == 'ind' ) } }
        elif msg.id not in list( gReactVal.reactSetInd[ ctx.guild.id ].keys() ):
            gReactVal.reactSetInd[ ctx.guild.id ][ msg.id ] = { str( emoji ): ( emoji, role, type == 'ind' ) }
        else:
            gReactVal.reactSetInd[ ctx.guild.id ][ msg.id ][ str( emoji ) ] = ( emoji, role, type == 'ind' )

        await ReactionConfigSetting.sentMsgBaseData( ctx.send, ctx.guild, msg )

        s = save_to_sqlite( 'ind', ctx.guild.id, msg.id, str( emoji ), role.id, type )

        await msg.add_reaction( emoji=emoji.name )
        '''await ctx.send(
            f"{msg.content} at {msg.jump_url}\n{emoji.name} for :{emoji.name}:\n{role.mention}\n{ctx.author.mention}\
            \nWrite SQL with {s}" )'''
        await ctx.send(
            (
                f"{ctx.author.mention} set {'independence' if type=='ind' else 'disjointness'} {emoji} with",
                f" {role.mention} at {m if len(m:=msg.content) else (m[:7] +'...')} that Write SQL with {s}" ) )

    @reaction_relationship.command( name='write_ind', aliases=[ 'wi' ] )
    async def write_ind( self, ctx: commands.Context, msg: discord.Message, emoji: str, role: discord.Role ):
        await self.write_raw( ctx, msg, emoji, role, 'ind' )

    @reaction_relationship.command( name='write_disj', aliases=[ 'wd' ] )
    async def write_disj( self, ctx: commands.Context, msg: discord.Message, emoji: str, role: discord.Role ):
        await self.write_raw( ctx, msg, emoji, role, 'disj' )


def setup( bot: commands.Bot ):
    bot.add_cog( ReactionConfigSetting( bot ) )
