# https://www.postgresqltutorial.com/postgresql-python/
# https://www.postgresql.org/docs/9.2/sql-insert.html

from flask import Flask, request, redirect, jsonify, session
import psycopg2
from config import config

PORT = 8080

app = Flask(__name__)
app.debug = True
params = config()
conn = psycopg2.connect(**params)
# create a cursor
cur = conn.cursor()

userIDs =  {}

INSERT_USER = """ INSERT INTO auction_user VALUES (%s, %s) """

# request.get_json() -> GET DATA
# instalar docker

@app.route('/user', methods=['GET', 'POST', 'PUT'])
def user():
    if request.method == 'POST': # {“username”: username, “password”:password} -> mudar para também receber mail
        return insert_auction_user(**request.get_json())
    elif request.method == 'GET':
        return 'GET'
    else:
        return 'PUT'
    return

@app.route('/leilao', methods=['POST'])
def leilao():
    return request.get_json()

@app.route('/leilao/<leilaoId>', methods=['GET'])
def leiloes_k(leilaoId):
    return f'leilao {leilaoId}'

@app.route('/leilao/<leilaoId>', methods=['PUT'])
def leilao_edit():
    return 'leilao edit'

@app.route('/leiloes' , methods=['GET'])
def leiloes():
    return 'leiloes'

@app.route('/licitar/<leilaoId>/<licitacao>', methods=['GET'])
def licitar(leilaoId, licitacao):
    return f'leilao {leilaoId}'


def insert_auction_user(username, password):
    try :
        cur.execute(INSERT_USER, (username, password,))
        conn.commit()
        token = str(len(userIDs)) # está mal -> ver melhor
        #userIDs[token] = username
        return {"userId": str(token)}
    except Exception as e:
        return {"erro": '{m}'.format(m = str(e))}

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
    try :
        print('Connecting to the PostgreSQL database...')

	# close the communication with the PostgreSQL
        #cur.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

    app.run(port=PORT)