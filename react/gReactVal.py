import sqlite3
import discord
import os


class DefaultEmoji():

    def __init__( self, name ):
        self.name = name

    def __str__( self ) -> str:
        return self.name


reactSetInd = {}


async def activeFunction( send, guild: discord.Guild ):
    error_code = ''
    conn = sqlite3.connect( os.path.join( os.path.dirname( __file__ ) + '\\reaction.db' ) )
    cursor = conn.cursor()
    for row in cursor.execute( f"SELECT msg, emoji, role, type='ind' FROM ind WHERE guild={guild.id}" ):
        #print( [ str( x ) for x in guild.emojis ] )
        #print( row[ 1 ] )
        try:
            emoji = list( filter( lambda x: str( x ) == row[ 1 ], guild.emojis ) )[ 0 ]
        except IndexError:
            emoji = DefaultEmoji( row[ 1 ] )

        if ( role := guild.get_role( row[ 2 ] ) ) is None:
            error_code += '\n' + str( row ) + ' => this role is unavailable'
            continue

        if isinstance( emoji, DefaultEmoji ) and '<' in str( emoji ):
            error_code += '\n' + str( row ) + ' => this emoji is unavailable'
            print( f"{str(emoji) =} , {type(emoji) =}" )
            continue

        if guild.id not in list( reactSetInd.keys() ):
            reactSetInd[ guild.id ] = { row[ 0 ]: { row[ 1 ]: ( emoji, role, row[ 3 ] == 1 ) } }
        elif row[ 0 ] not in list( reactSetInd[ guild.id ].keys() ):
            reactSetInd[ guild.id ][ row[ 0 ] ] = { row[ 1 ]: ( emoji, role, row[ 3 ] == 1 ) }
        else:
            reactSetInd[ guild.id ][ row[ 0 ] ][ row[ 1 ] ] = ( emoji, role, row[ 3 ] == 1 )
    await send( f"loaded ! {('below sq was broke and not be loaded' + error_code ) if error_code != '' else ''}" )
    conn.close()

    print( reactSetInd )
