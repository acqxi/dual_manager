import asyncio
import random as rd
import re
from abc import abstractmethod, abstractstaticmethod
from typing import Union

import discord
from discord.ext import commands


class BaseChessGame():
    POS = None
    POS_I = None

    def __init__( self, player1, player2 ) -> None:
        self.p1 = player1
        self.p2 = player2
        self.last_gamer = None
        self.who = { player1: 0, player2: 1 }
        self.whol = [ player1, player2 ]
        self.go = None

    @property
    def left_place( self ) -> tuple:
        return tuple( [ id for id, i in enumerate( self.go ) if i is None ] )

    def is_here_empty( self, pos ) -> bool:
        return self.go[ pos ] is None

    def place( self, player, pos ) -> bool:
        if not self.is_here_empty( pos ):
            return False
        self.go[ pos ] = self.who[ player ]
        return True

    @abstractmethod
    def gameover( self ) -> Union[ int, None ]:
        return None

    def __iter__( self ):
        return self

    @abstractmethod
    def __next__( self ):
        if ( last_gamer_symbol := self.gameover() ) is not None:
            self.last_gamer = self.whol[ last_gamer_symbol ]
            raise StopIteration
        return tuple( self.go )

    @abstractstaticmethod
    def gui( go ) -> str:
        return str( go )


class PopUpPirate( BaseChessGame ):
    POS = [
        [ '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣' ],
        [ '0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '▶', '◀', '🔼', '🔽', '⏸', '⏹' ]
    ]
    POS_I = [ { v: i for i, v in enumerate( POS[ 0 ] ) }, { v: i for i, v in enumerate( POS[ 1 ] ) } ]

    def __init__( self, player1, player2, player3=None, size=0 ) -> None:
        super().__init__( player1, player2 )
        self.p3 = player3
        self.size = size
        self.who = { player1: 0, player2: 1, player3: 2 }
        self.whol = [ player1, player2, player3 ]
        self.go = [ None ] * [ 9, 16 ][ size ]
        self.bomb = rd.randint( 0, [ 8, 15 ][ size ] )

    def gameover( self ) -> Union[ int, None ]:
        if self.go[ self.bomb ] is not None:
            return self.go[ self.bomb ]
        return None

    @staticmethod
    def gui( go ) -> str:
        anno = ''
        for index, i in enumerate( go ):
            anno += { None: PopUpPirate.POS[ { 9: 0, 16: 1 }[ len( go ) ] ][ index ], 0: '⭕', 1: '❌', 2: '💢' }[ i ] + ' '
            anno += '\n' if ( index + 1 ) % { 9: 3, 16: 4 }[ len( go ) ] == 0 else ''
        return anno


class TieTacToe( BaseChessGame ):

    POS_I = { '1️⃣': 0, '2️⃣': 1, '3️⃣': 2, '4️⃣': 3, '5️⃣': 4, '6️⃣': 5, '7️⃣': 6, '8️⃣': 7, '9️⃣': 8 }
    POS = [ '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣' ]

    def __init__( self, player1, player2 ) -> None:
        super().__init__( player1, player2 )
        self.go = [ None ] * 9
        self.whol = [ player1, player2, 'tie' ]
        self.line = []

    def gameover( self ) -> Union[ int, None ]:
        END_STEP = [ [ 0, 3, 6 ], [ 1, 4, 7 ], [ 2, 5, 8 ], [ 0, 1, 2 ], [ 4, 5, 3 ], [ 7, 8, 6 ], [ 0, 4, 8 ], [ 2, 4, 6 ] ]
        for i in END_STEP:
            if self.go[ i[ 0 ] ] is None:
                continue
            if self.go[ i[ 0 ] ] != self.go[ i[ 1 ] ]:
                continue
            if self.go[ i[ 0 ] ] != self.go[ i[ 2 ] ]:
                continue
            self.line = i
            return self.go[ i[ 0 ] ]
        if None not in self.go:
            return 2
        return None

    @staticmethod
    def gui( go ) -> str:
        anno = ''
        for index, i in enumerate( go ):
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
    @commands.command( name='tic-tac-toe', aliases=[ '3t', 'ttt', 'ox', 'ooxx', '井字棋', '圈圈叉叉' ] )
    async def tic_tac_toe( self, ctx: commands.Context, antagonist: Union[ discord.Member, str ], *args ):
        wait_time = 30
        if args:
            if args[ -1 ].startswith( '-t=' ):
                wait_time = eval( args[ -1 ].split( '=' )[ -1 ] )
            if args[ -1 ].startswith( '限時' ):
                wait_time = eval( re.findall( r"\d+\.?\d*", args[ -1 ] )[ 0 ] )
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
                        f"供玩家 思考/反應/手殘 的時間 : {wait_time} 秒",
                    ] ) )
        elif isinstance( antagonist, str ) and antagonist in [
                'god',
                'dog',
                'mid',
                'dim',
                'noob',
                'boon',
                '神',
                '狗',
                '新手',
                '剛玩',
                '弱雞',
                '辣雞',
        ]:
            antagonist = BotMember( antagonist )
            head_msg = await ctx.send(
                ''.join(
                    [
                        f"{antagonist.mention} is ❌ and will not react msg\n",
                        f"玩家{ctx.author.mention} is ⭕\n",
                        f"供玩家 思考/反應/手殘 的時間 : {wait_time} 秒",
                    ] ) )
        else:
            head_msg = await ctx.send( '能陪你玩的機器人有： god, dog, mid, dim, noob, boon, 神, 狗, 新手, 剛玩, 弱雞, 辣雞' )
            return

        ga = TieTacToe( ctx.author, antagonist )
        turn = -1 if isinstance( antagonist, BotMember ) and antagonist.name in [ 'dog', 'dim', 'boon' ] else 1
        playerlist = [ None, ctx.author, antagonist ]
        go_gui = await ctx.send( '棋盤顯示區域' )
        allow_pos = await ctx.send( '合法輸入及反應區域' )
        [ await allow_pos.add_reaction( emoji ) for emoji in TieTacToe.POS ]
        for go in ga:
            turn *= -1

            if isinstance( antagonist, BotMember ) and turn == -1:
                flag = None
                if antagonist.name in [ 'god', 'dog', 'dim', 'mid', '神', '狗', '新手', '剛玩' ]:
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

                        if flag is not None and antagonist.name in [ 'dim', 'mid', '新手', '剛玩' ]:
                            break
                        elif flag is not None and go[ flag ] == 1:
                            break
                        else:
                            continue
                if antagonist.name in [ 'god', 'dog', '神', '狗' ]:
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
                            f"{antagonist.mention} is ❌ and will not react msg\n",
                            f"玩家{ctx.author.mention} is ⭕\n",
                            f"供玩家 思考/反應/手殘 的時間 : {wait_time} 秒\n",
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
        await go_gui.edit( content=TieTacToe.gui( ga.go ) )
        await allow_pos.edit( content='GameOver / 遊戲結束' )
        if ga.last_gamer is None:
            await ctx.send( f"{playerlist[ turn *-1 ].mention} 贏了這場比賽, 因為 {playerlist[ turn ].mention} 睡著錯過時間啦" )
            return
        await ctx.send(
            f'{ctx.author.mention}與{antagonist.mention}打成了平手' if isinstance( ga.last_gamer, str ) else (
                ga.last_gamer.mention + f" 贏了對手，他在 {' '.join([TieTacToe.POS[i] for i in ga.line])} 下了勝利的一手" ) )

    @commands.command( name='pop-up-pirate', aliases=[ 'pup', '海盜桶' ] )
    async def pop_up_pirate( self, ctx: commands.Context, *args ):
        wait_time = 30
        player3, antagonist, size = None, None, 0
        if args:
            args = [ arg for arg in args if arg is not None ]
            args_flag = 0
            print( args )
            await ctx.send( f"```{args}```" )

            if args[ -1 ].startswith( '-t=' ):
                wait_time = eval( args[ -1 ].split( '=' )[ -1 ] )
                args_flag += 1
            if args[ -1 ].startswith( '限時' ):
                wait_time = eval( re.findall( r"\d+\.?\d*", args[ -1 ] )[ 0 ] )
                args_flag += 1

            if '大棋盤' in args:
                size = 1
                args_flag += 1

            if len( args ) <= args_flag:
                ctx.send( 'XXXXXXXXXXXXXXXXXXXXXX1' )
                return

            if args[ 0 ].startswith( '<@!' ) or args[ 0 ].startswith( '<@' ):
                antagonist = ctx.guild.get_member( eval( args[ 0 ].strip( '<@!>' ) ) )
                print( 'one person' )
            elif args[ 0 ] in [ 'god', 'dog', 'mid', 'noob', '神', '狗', '新手', '弱雞' ]:
                # 95     80     50      25
                antagonist = BotMember( args[ 0 ] )
            else:
                head_msg = await ctx.send( '能陪你玩的機器人1有： god, dog, mid, noob, 神, 狗, 新手,  弱雞' )
                return

            if len( args ) > 1 + args_flag:
                if args[ 1 ].startswith( '<@!' ) or args[ 1 ].startswith( '<@' ):
                    player3 = ctx.guild.get_member( eval( args[ 1 ].strip( '<@!>' ) ) )
                elif args[ 1 ] in [ 'god', 'dog', 'mid', 'noob', '神', '狗', '新手', '弱雞' ]:
                    player3 = BotMember( args[ 1 ] )
                else:
                    head_msg = await ctx.send( '能陪你玩的機器人2有： god, dog, mid, noob, 神, 狗, 新手,  弱雞' )
                    return
        else:
            ctx.send( 'XXXXXXXXXXXXXXXXXXXXXX0' )
            return

        if isinstance( antagonist, discord.Member ) or isinstance( player3, discord.Member ):
            player_list_str = ' 、 '.join(
                [ member.mention for member in ( antagonist, player3 ) if isinstance( member, discord.Member ) ] )
            player_list_set = { member for member in ( antagonist, player3 ) if isinstance( member, discord.Member ) }
            player_acc_set = set()
            head_msg = await ctx.send( f"請問玩家 {player_list_str} 是否要與玩家 {ctx.author.mention} 玩海盜桶，是請按O反應本段文字，30秒內未反應則邀請失效" )
            [ await head_msg.add_reaction( emoji ) for emoji in [ '⭕', '❌' ] ]
            for player in player_list_set:
                try:
                    reaction, user = await self.bot.wait_for(
                        event='reaction_add',
                        check=lambda r, u: u in player_list_set.difference( player_acc_set ) and r.emoji in [ '⭕', '❌' ] and r.
                        message == head_msg,
                        timeout=30 )
                except asyncio.TimeoutError as e:
                    await head_msg.edit( content=f"玩家{ctx.author.mention}向玩家{player_list_str}發起的戰鬥邀請失效{e}" )
                    return
                if reaction.emoji == '⭕':
                    player_acc_set.add( user )
                else:
                    await head_msg.edit( content=f"玩家{ctx.author.mention}向玩家{player_list_str}發起的戰鬥邀請被拒絕" )
                    return
        head_msg = await ctx.send(
            ''.join(
                [
                    ( '' if isinstance( antagonist, BotMember ) else '玩家 ' ) + antagonist.mention + ' is ❌ ',
                    'and will not react msg \n' if isinstance( antagonist, BotMember ) else '\n',
                    ( '' if isinstance( player3, BotMember ) else '玩家 ' ) if player3 is not None else '',
                    ( player3.mention + 'is 💢 ' ) if player3 is not None else '',
                    ( 'and will not react msg \n' if isinstance( player3, BotMember ) else '\n' )
                    if player3 is not None else '',
                    f"玩家 {ctx.author.mention} is ⭕\n",
                    f"供玩家 思考/反應/手殘 的時間 : {wait_time} 秒",
                ] ) )

        ga = PopUpPirate( ctx.author, antagonist, player3, size=size )
        player_lo = [ member for member in [ ctx.author, antagonist, player3 ] if member is not None ]
        p2e = { ctx.author: '⭕', antagonist: '❌', player3: '💢' }
        rd.shuffle( player_lo )
        turn = 0
        go_gui = await ctx.send( '棋盤顯示區域' )
        allow_pos = await ctx.send( '合法輸入及反應區域' )
        discord.Message.add_reaction
        [ await allow_pos.add_reaction( emoji ) for emoji in ga.POS[ size ] ]
        for go in ga:
            turn += 1
            on_play = player_lo[ turn % len( player_lo ) ]
            place = None
            await go_gui.edit( content='👉🏻 ' + p2e[ on_play ] + '\n\n' + ga.gui( go ) )
            if isinstance( on_play, BotMember ):
                is_boom = rd.randint( 0, 99 ) > {
                    'god': 95,
                    'dog': 80,
                    'mid': 50,
                    'noob': 25,
                    '神': 95,
                    '狗': 80,
                    '新手': 50,
                    '弱雞': 25
                }[ on_play.name ] or len( ga.left_place ) <= 1
                option_place = list( ga.left_place )
                option_place.remove( ga.bomb )
                place = ga.bomb if is_boom else rd.choice( option_place )
            else:
                left_emoji = [ ga.POS[ size ][ i ] for i in ga.left_place ]
                await allow_pos.edit(
                    content=''.join(
                        [
                            on_play.mention + '你可以反應此訊息',
                            ' or '.join( left_emoji ),
                            '來填入屬於你的符號(' + p2e[ on_play ] + ')',
                        ] ) )
                try:
                    place_emoji, user = await self.bot.wait_for(
                        event='reaction_add',
                        check=lambda r, u: u == on_play and r.emoji in left_emoji and r.message == allow_pos,
                        timeout=wait_time )
                except asyncio.TimeoutError:
                    break
                place = ga.POS_I[ size ][ place_emoji.emoji ]
            ga.place( player=on_play, pos=place )
        await go_gui.edit( content=ga.gui( ga.go ) )
        await allow_pos.edit( content='GameOver / 遊戲結束' )
        await ctx.send( ga.last_gamer.mention + f" 踩爆了唯一一顆地雷，被炸暈在 {ga.POS[size][ga.bomb]} 了。" )


def setup( bot ):
    bot.add_cog( Test( bot ) )
