# https://www.postgresqltutorial.com/postgresql-python/
# https://www.postgresql.org/docs/9.2/sql-insert.html

from flask import Flask, request, redirect, jsonify, session
import psycopg2
from config import config
import string
import random

PORT = 8080

app = Flask(__name__)
app.debug = True
params = config()
conn = psycopg2.connect(**params)
# create a cursor
cur = conn.cursor()

userIDs =  {}

INSERT_USER = """ INSERT INTO auction_user VALUES (%s, %s) """
SELECT_AUCTIONS = " SELECT id, description FROM auction "
INSERT_AUCTION = " INSERT INTO auction(title, description, id, biddding) VALUES (%s, %s, %s, %.2f) " # MAL!!!

# request.get_json() -> GET DATA
# instalar docker

def generate_EAN():
    letters = string.digits
    return ''.join(random.choice(letters) for i in range(13))

@app.route('/user', methods=['POST', 'PUT'])
def user():
    if request.method == 'POST': # {“username”: username, “password”:password} -> mudar para também receber mail
        return insert_auction_user(**request.get_json())
    else:
        return autentication_auction_user(**request.get_json())
    return

@app.route('/leilao', methods=['POST'])
def leilao():
    args = request.get_json()
    if args!=None and len(args)==4:
        return create_auction(**args)
    return {"erro":"Wrong number of arguments"}

@app.route('/leilao/<leilaoId>', methods=['GET','PUT'])
def leiloes_k(leilaoId):
    return

@app.route('/leiloes' , methods=['GET'])
def leiloes():
    cur.execute(SELECT_AUCTIONS)
    auctions = cur.fetchone()
    conn.commit()
    if auctions == None:
        return {}
    return auctions # DOESN'T WORK

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
    sql = """ SELECT username, password  FROM auction_user where username=%s"""
    cur.execute(sql, (username,))
    try:
        if password!=cur.fetchone()[1]:
            return 'Wrong password'
    except:
       return 'Wrong username'
    return "Successful authentication"

def create_auction(artigoId, precoMinimo, titulo, descricao): # pode receber outros argumentos
    try:
        print (precoMinimo)
        insert = f" INSERT INTO auction (title, description, id, bidding, auction_user_username) VALUES ('{titulo}', '{descricao}', '{artigoId}', {precoMinimo}, 'DEBUG')" # CHANGE
        print(insert)
        cur.execute(insert)
        conn.commit()
        return {"leilaoId": "coisa"}
    except Exception as e:
        return {"erro": '{m}'.format(m = str(e))}


if __name__ == '__main__':
    try :
        print('Connecting to the PostgreSQL database...')

	# close the communication with the PostgreSQL
        #cur.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

    app.run(port=PORT)