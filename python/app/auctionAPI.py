# POSTGRESQL & PSYCOPG2
# https://www.postgresqltutorial.com/postgresql-python/
# https://www.postgresql.org/docs/9.2/sql-insert.html
# https://www.psycopg.org/docs/usage.html

#FLASK
# https://flask.palletsprojects.com/en/1.1.x/quickstart/

# JWT & AUTHENTICATION
# https://pyjwt.readthedocs.io/en/stable/
# https://dev.to/aminu_israel/using-json-web-token-jwt-with-python-3n4p
# https://steelkiwi.com/blog/jwt-authorization-python-part-1-practise/


from flask import Flask, request, redirect, jsonify, session
import psycopg2, logging
from config import config
import datetime
import jwt

# INITIALIZATIONS
app = Flask(__name__)
app.debug = True
app.secret_key = 'key'
params = config()
JWT_SECRET = 'secret'
JWT_ALGORITHM = 'HS256'
#JWT_EXP_DELTA_SECONDS = 20

# SQL COMMANDS
INSERT_USER = """ INSERT INTO auction_user VALUES (%s, %s) """
SELECT_AUCTIONS = " SELECT id, description FROM auction "
INSERT_AUCTION = " INSERT INTO auction(title, description, id, biddding) VALUES (%s, %s, %s, %.2f) "
SELECT_USER = """ SELECT username, password  FROM auction_user where username=%s"""

# FLASK METHODS

@app.route('/user', methods=['POST', 'PUT'])
def user():
    if(request.get_json()!=None):
        if request.method == 'POST': # {“username”: username, “password”:password} -> mudar para também receber mail
            return insert_auction_user(**request.get_json())
        else:
            return autentication_auction_user(**request.get_json()) # fazer verificação
    return {"bye": "bye"}

@app.route('/leilao', methods=['POST'])
def leilao():
    args = request.get_json()
    if args!=None and len(args)==5:
        return create_auction(**args)
    return {"erro": "Wrong number of arguments"}

@app.route('/leilao/<leilaoId>', methods=['GET','PUT'])
def leiloes_k(leilaoId):
    return

@app.route('/leiloes' , methods=['GET'])
def leiloes():
    conn = db_connection()
    # create a cursor
    cur = conn.cursor()
    cur.execute(SELECT_AUCTIONS)
    auctions = cur.fetchone()
    conn.commit()
    cur.close()
    if auctions == None:
        return {}
    return auctions # DOESN'T WORK

@app.route('/licitar/<leilaoId>/<licitacao>', methods=['GET'])
def licitar(leilaoId, licitacao):
    return f'leilao {leilaoId}'


# FUNCTIONS

# ? done
def insert_auction_user(username, password):
    try :
        conn = db_connection()
        # create a cursor
        cur = conn.cursor()
        cur.execute(INSERT_USER, (username, password,))
        conn.commit()
        new_id = cur.fetchone()[0]
        cur.close()
        return {"userId": new_id}
    except Exception as e:
        return {"erro": '{m}'.format(m = str(e))}

# TODO
def autentication_auction_user(username, password):
    if match_password(username, password):
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=90),
            'iat': datetime.datetime.utcnow(),
            'sub': username
        }
        encoded = jwt.encode(
            payload,
            JWT_SECRET,
            algorithm=JWT_ALGORITHM
        )
        session['authToken'] = encoded
        return {"auth": encoded}
    return {"error": "Wrong data"}

def match_password(username, password):
    conn = db_connection()
    cur = conn.cursor()
    cur.execute(SELECT_USER, (username,))
    try:
        if password!=cur.fetchone()[1]:
            cur.close()
            return False
    except:
        cur.close()
        return False
    cur.close()
    return True

def create_auction(artigoId, precoMinimo, titulo, descricao, data_de_fim):

    try:
        conn = db_connection()
        cur = conn.cursor()

        date = datetime.strptime(data_de_fim, '%m/%d/%Y')
        today = datetime.now()
        if today > date:
            return {"erro": 'Data incorreta'}  # colocar data default?

        # username = session['token']
        username = "username"  # colocar session!!!!
        insert = """ INSERT INTO auction (title, description, id, bidding, finish_date, auction_user_username) 
                VALUES (%s, %s, %s, %s, %s, %s)"""
        values = (titulo, descricao, artigoId, precoMinimo, date, username)
        cur.execute(insert, values)

        conn.commit()
        cur.close()
        return {"leilaoId": artigoId}

    except Exception as e:
        return {"erro": '{m}'.format(m=str(e))}

# * DONE
def db_connection():
    db = psycopg2.connect(**params)
    return db

# * DONE
if __name__ == "__main__":

    # Set up the logging
    logging.basicConfig(filename="logs/log_file.log")
    logger = logging.getLogger('logger')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s [%(levelname)s]:  %(message)s',
                              '%H:%M:%S')
                              # "%Y-%m-%d %H:%M:%S") # not using DATE to simplify
    ch.setFormatter(formatter)
    logger.addHandler(ch)



    logger.info("\n---------------------------------------------------------------\n" + 
                  "API v1.0 online: http://localhost:8080/\n\n")


    app.run(host="0.0.0.0", debug=True, threaded=True)

