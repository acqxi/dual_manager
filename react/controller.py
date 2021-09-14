import os
import sqlite3

import psycopg2

from . import gReactVal

conn = psycopg2.connect( **gReactVal.conn_parse )

print( os.path.join( os.path.dirname( __file__ ) + '\\reaction.db' ) )

c = conn.cursor()

c.execute( "CREATE TABLE IF NOT EXISTS single_role (msg integer, emoji text, role integer)" )

#conn.commit()

#c.execute( "INSERT INTO single_role VALUES ('123456789','王小寶','321654879')" )
#c.execute( "INSERT INTO single_role VALUES ('984351168','吳有明','416846615')" )
#c.execute( "INSERT INTO single_role VALUES ('135416846','白采君','168135123')" )

#conn.commit()
#c.execute( 'DELETE FROM single_role' )

for row in c.execute( 'SELECT * FROM ind ORDER BY msg' ):
    print( row )

for row in c.execute( "SELECT emoji, type='ind' FROM ind" ):
    print( 'OC => ' + str( row ) )

conn.close()
