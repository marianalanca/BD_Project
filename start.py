# https://www.postgresqltutorial.com/postgresql-python/

from flask import Flask
import psycopg2
from config import config

app = Flask(__name__)

'''@app.route('/')
def index():
    return 0

@app.route('/<name>')
def hello_name(name):
    return "Hello {}!".format(name)'''

if __name__ == '__main__':
    # passar para database.ini
    try :
        params = config()
        #conn = psycopg2.connect(**params)
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params) # aceder à BD

        # create a cursor
        cur = conn.cursor()

        # execute a statement
        print('PostgreSQL database version:')
        cur.execute('SELECT version()')

        # display the PostgreSQL database server version
        db_version = cur.fetchone()
        print(db_version)

	# close the communication with the PostgreSQL
        cur.close()


    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

    # criar BD!

    app.run()