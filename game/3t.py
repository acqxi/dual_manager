import asyncio
import random as rd
from typing import Union

import discord
from discord.ext import commands


class TieTacToe():

    POS_I = { '1️⃣': 0, '2️⃣': 1, '3️⃣': 2, '4️⃣': 3, '5️⃣': 4, '6️⃣': 5, '7️⃣': 6, '8️⃣': 7, '9️⃣': 8 }
    POS = [ '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣' ]

    def __init__( self, player1, player2 ) -> None:
        self.p1 = player1
        self.p2 = player2
        self.winner = None
        self.game = [ None ] * 9
        self.line = []

    @property
    def left_place( self ) -> tuple:
        return tuple( [ id for id, i in enumerate( self.game ) if i is None ] )

    def is_here_empty( self, pos ) -> bool:
        return self.game[ pos ] is None

    def place( self, player, pos ) -> bool:
        if not self.is_here_empty( pos ):
            return False
        self.game[ pos ] = 0 if player == self.p1 else 1
        return True

    def gameover( self ) -> Union[ int, None ]:
        END_STEP = [ [ 0, 3, 6 ], [ 1, 4, 7 ], [ 2, 5, 8 ], [ 0, 1, 2 ], [ 4, 5, 3 ], [ 7, 8, 6 ], [ 0, 4, 8 ], [ 2, 4, 6 ] ]
        for i in END_STEP:
            if self.game[ i[ 0 ] ] is None:
                continue
            if self.game[ i[ 0 ] ] != self.game[ i[ 1 ] ]:
                continue
            if self.game[ i[ 0 ] ] != self.game[ i[ 2 ] ]:
                continue
            self.line = i
            return self.game[ i[ 0 ] ]
        if None not in self.game:
            return 2
        return None

    def __iter__( self ):
        return self

    def __next__( self ):
        if ( winner := self.gameover() ) is not None:
            self.winner = [ self.p1, self.p2, 'TIE' ][ winner ]
            raise StopIteration
        return tuple( self.game )

    @staticmethod
    def gui( game ) -> str:
        anno = ''
        for index, i in enumerate( game ):
            anno += { None: TieTacToe.POS[ index ], 0: '⭕', 1: '❌' }[ i ] + ' '
            anno += '\n' if index % 3 == 2 else ''
        return anno


class BotMember():

    def __init__( self, name ):
        self.name = name
        self.mention = f' ${name} '


class Test( commands.Cog ):

    def __init__( self, bot: commands.Bot ) -> None:
        self.bot = bot
        super().__init__()

    async def cog_check( self, ctx ):
        return True

    #@commands.Cog.listener()
    async def on_raw_reaction_add( self, rRED: discord.RawReactionActionEvent ):
        ch = self.bot.get_guild( rRED.guild_id ).get_channel( rRED.channel_id )
        await ch.send( f"{rRED.emoji=}\n{rRED.emoji.name == '⭕'}" )

    # @commands.group(name='tic-tac-toe',aliases = ['3t','ttt','ox','ooxx'])
    @commands.command( name='tic-tac-toe', aliases=[ '3t', 'ttt', 'ox', 'ooxx' ] )
    async def tic_tac_toe( self, ctx: commands.Context, antagonist: Union[ discord.Member, str ], *args ):
        wait_time = 10
        if args:
            if args[ -1 ].startswith( '-t=' ):
                wait_time = eval( args[ -1 ].split( '=' )[ -1 ] )
        if isinstance( antagonist, discord.Member ):
            head_msg = await ctx.send( f"請問玩家{antagonist.mention}是否要與玩家{ctx.author.mention}玩井字棋，是請按O反應本段文字，30秒內未反應則邀請失效" )
            [ await head_msg.add_reaction( emoji ) for emoji in [ '⭕', '❌' ] ]
            try:
                reaction, user = await self.bot.wait_for(
                    event='reaction_add',
                    check=lambda r, u: u == antagonist and r.emoji in [ '⭕', '❌' ] and r.message == head_msg,
                    timeout=30 )
            except asyncio.TimeoutError as e:
                await head_msg.edit( content=f"玩家{ctx.author.mention}向玩家{antagonist.mention}發起的戰鬥邀請失效{e}" )
                return
            if reaction.emoji != '⭕':
                return
            await head_msg.edit(
                content=''.join(
                    [
                        f"玩家{antagonist.mention} is ❌\n",
                        f"玩家{ctx.author.mention} is ⭕\n",
                        f"timeout : {wait_time}",
                    ] ) )
        elif isinstance( antagonist, str ) and antagonist in [ 'god', 'dog', 'mid', 'dim', 'noob', 'boon' ]:
            antagonist = BotMember( antagonist )
            head_msg = await ctx.send(
                ''.join( [
                    "bot is ❌ and will not react msg\n",
                    f"玩家{ctx.author.mention} is ⭕\n",
                    f"timeout : {wait_time}",
                ] ) )
        else:
            head_msg = await ctx.send( 'unknown cmd ? bot only god, dog, mid, dim, noob, boon' )
            return

        ga = TieTacToe( ctx.author, antagonist )
        turn = -1 if isinstance( antagonist, BotMember ) and antagonist.name in [ 'dog', 'dim', 'boon' ] else 1
        playerlist = [ None, ctx.author, antagonist ]
        go_gui = await ctx.send( 'game start' )
        allow_pos = await ctx.send( 'game start' )
        for go in ga:
            turn *= -1

            if isinstance( antagonist, BotMember ) and turn == -1:
                if antagonist.name in [ 'god', 'dog', 'dim', 'mid' ]:
                    flag = None
                    END_STEP = [
                        [ 0, 3, 6 ], [ 1, 4, 7 ], [ 2, 5, 8 ], [ 0, 1, 2 ], [ 4, 5, 3 ], [ 7, 8, 6 ], [ 0, 4, 8 ], [ 2, 4, 6 ]
                    ]
                    rd.shuffle( END_STEP )
                    for i in END_STEP:
                        if go[ i[ 0 ] ] == go[ i[ 1 ] ] and go[ i[ 0 ] ] is not None and i[ 2 ] in ga.left_place:
                            flag = i[ 2 ]
                        if go[ i[ 2 ] ] == go[ i[ 1 ] ] and go[ i[ 1 ] ] is not None and i[ 0 ] in ga.left_place:
                            flag = i[ 0 ]
                        if go[ i[ 0 ] ] == go[ i[ 2 ] ] and go[ i[ 0 ] ] is not None and i[ 1 ] in ga.left_place:
                            flag = i[ 1 ]

                        if flag is not None and antagonist.name in [ 'dim', 'mid' ]:
                            break
                        elif flag is not None and go[ flag ] == 1:
                            break
                        else:
                            continue
                if antagonist.name in [ 'god', 'dog' ]:
                    if flag is None:
                        for i in [ 4, 8, 6, 2, 0, 1, 5, 3, 7 ]:
                            if i in ga.left_place:
                                flag = i
                                break
                else:
                    if flag is None:
                        flag = rd.choice( ga.left_place )
                ga.place( player=playerlist[ turn ], pos=flag )
                await head_msg.edit(
                    content=''.join(
                        [
                            "bot is ❌ and will not react msg\n",
                            f"玩家{ctx.author.mention} is ⭕\n",
                            f"timeout : {wait_time}\n",
                            f"bot place {TieTacToe.POS[ flag ]}",
                        ] ) )

            else:
                left_emoji = [ TieTacToe.POS[ i ] for i in ga.left_place ]
                await go_gui.edit( content=[ '', '👉🏻 ⭕\n\n', '👉🏻 ❌\n\n' ][ turn ] + TieTacToe.gui( go ) )

                # await go_gui.clear_reactions()
                # [ await go_gui.add_reaction( emoji ) for emoji in left_emoji ]
                await allow_pos.edit(
                    content=''.join(
                        [
                            playerlist[ turn ].mention,
                            '你可以反應此訊息',
                            ' or '.join( left_emoji ),
                            '來填入屬於你的符號(',
                            [ '', '⭕', '❌' ][ turn ],
                            ')',
                        ] ) )
                try:
                    place_emoji, user = await self.bot.wait_for(
                        event='reaction_add',
                        check=lambda r, u: u == playerlist[ turn ] and r.emoji in left_emoji and r.message == allow_pos,
                        timeout=wait_time )
                except asyncio.TimeoutError:
                    break
                ga.place( player=playerlist[ turn ], pos=TieTacToe.POS_I[ place_emoji.emoji ] )
        await go_gui.edit( content=TieTacToe.gui( ga.game ) )
        await allow_pos.edit( content='GameOver' )
        if ga.winner is None:
            await ctx.send( f"{playerlist[ turn *-1 ].mention} is winner, Cuz {playerlist[ turn ].mention} is timeout" )
            return
        await ctx.send(
            f'{ctx.author.mention}與{antagonist.mention}打成了平手' if isinstance( ga.winner, str ) else (
                ga.winner.mention + f" is winner!!! who placed {' '.join([TieTacToe.POS[i] for i in ga.line])}" ) )


def setup( bot ):
    bot.add_cog( Test( bot ) )
