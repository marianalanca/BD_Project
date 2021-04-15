# https://www.postgresqltutorial.com/postgresql-python/

from flask import Flask
import psycopg2
from config import config

app = Flask(__name__)
params = config()
conn = psycopg2.connect(**params)
# create a cursor
cur = conn.cursor()

'''@app.route('/')
def index():
    return 0

@app.route('/<name>')
def hello_name(name):
    return "Hello {}!".format(name)'''

def insert_auction_user(username, password):
    try :
        sql = """ insert into auction_user VALUES (%s, %s)"""
        cur.execute(sql, (username, password))
        conn.commit()
        #print(cur.fetchone()[0])
    except:
        print('Could not insert new user')
    return

def autentication_auction_user(username, password):
    #try :
    sql = """ SELECT username, password  FROM auction_user where username=%s"""
    cur.execute(sql, (username,))
    try:
        if password!=cur.fetchone()[1]:
            print('Wrong password')
    except:
       print('Wrong username')
    return
if __name__ == '__main__':
    # passar para database.ini
    try :
        print('Connecting to the PostgreSQL database...')

        # insert_auction_user('nov1o', '1213')
        autentication_auction_user('marina','pass')

	# close the communication with the PostgreSQL
        cur.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

    #app.run()