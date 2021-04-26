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

DIV = "\n---------------------------------------------------------------\n"

# SQL COMMANDS
INSERT_USER = """ INSERT INTO auction_user VALUES (%s, %s) """
SELECT_AUCTIONS = " SELECT id, description FROM auction "
INSERT_AUCTION = " INSERT INTO auction(title, description, id, biddding) VALUES (%s, %s, %s, %.2f) "
SELECT_USERDATA = """ SELECT username, password  FROM auction_user where username=%s"""
SELECT_USER = """ SELECT username  FROM auction_user where username=%s"""

# FLASK METHODS

# {“username”: username, “password”:password}
# TODO MELHORAR
@app.route('/user', methods=['POST', 'PUT'])
def user():
    req = request.get_json()
    if(request.get_json()!=None and len(req)==2 and ('username' in req.keys()) and ('password' in req.keys())):
        if request.method == 'POST':
            return insert_auction_user(**req)
        else:
            return autentication_auction_user(**req) # fazer verificação
    logger.error(f'{DIV}Wrong Arguments\n')
    return {"erro": "Wrong arguments"}

@app.route('/leilao', methods=['POST'])
def leilao():
    args = request.get_json()
    if args!=None and len(args)==5:
        return create_auction(**args)
    return {"erro": "Wrong number of arguments"}

@app.route('/leilao/<leilaoId>', methods=['GET','PUT'])
def leiloes_k(leilaoId):
    return

# * TEM UM EXEMPLO DE AUTENTICAÇÃO!
# TODO
@app.route('/leiloes' , methods=['GET'])
def leiloes():
    try:
        if (authenticate(request.args['token'])):
            conn = db_connection()
            cur = conn.cursor()
            cur.execute(SELECT_AUCTIONS)
            auctions = cur.fetchone()
            conn.commit()
            cur.close()
            if auctions == None:
                return jsonify([])
            return jsonify([auctions])
        else:
            return {"error": "Invalid authentication"}
    except:
        return {"error": "Invalid authentication"}

@app.route('/licitar/<leilaoId>/<licitacao>', methods=['GET'])
def licitar(leilaoId, licitacao):
    return f'leilao {leilaoId}'

# TODO
@app.route('/licitar/messageBox', methods=['GET'])
def message():
    return

# ! DEBUG
@app.route('/DEBUG/token', methods=['GET'])
def token():
    try:
        if authenticate(request.args['token']):
            return {"hey": "oi"}
        return {"error": "Need to login"}
    except:
        log("ERROR: Need to Login")
        return {"error": "Need to Login"}

# FUNCTIONALITIES

# fazer log:  logger.info("\nclosed\n\n")

def insert_auction_user(username, password):
    try :
        conn = db_connection()
        # create a cursor
        cur = conn.cursor()
        cur.execute(INSERT_USER, (username, password,))
        conn.commit()
        new_id = cur.fetchone()[0]
        logger.info(f'{DIV}User {new_id} created successfuly\n')
        return {"userId": new_id}
    except Exception as e:
        error = '{m}'.format(m = str(e))
        logger.error(f'{DIV}{error}\n')
        return {"erro": error}
    finally:
        cur.close()

def autentication_auction_user(username, password):
    try:
        if match_password(username, password):
            encoded = encode(username)
            session['authToken'] = encoded
            logger.info(f'{DIV}Authentication token generated\n{encoded}\n')
            return {"authToken": encoded}
        logger.error(f'{DIV}Wrong data\n')
        return {"error": "Wrong data"}  # return json_response({'message': 'Wrong credentials'}, status=400)
    except Exception as e:
        error = '{m}'.format(m=str(e))
        logger.error(f'{DIV}{error}\n')
        return {"erro": error}

def match_password(username, password):
    conn = db_connection()
    cur = conn.cursor()
    cur.execute(SELECT_USERDATA, (username,))
    try:
        if password!=cur.fetchone()[1]:
            cur.close()
            return False
    except:
        cur.close()
        return False
    cur.close()
    return True

def find_user(username):
    try:
        conn = db_connection()
        cur = conn.cursor()
        cur.execute(SELECT_USERDATA, (username,))
        return jsonify(cur.fetchone()[1])
    except:
        return {}
    finally:
        cur.close()

def decode(encoded):
    return jwt.decode(encoded, JWT_SECRET, JWT_ALGORITHM)['sub']

def encode(value):
    payload = {
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=90),
        'iat': datetime.datetime.utcnow(),
        'sub': value
    }
    return jwt.encode(
        payload,
        JWT_SECRET,
        algorithm=JWT_ALGORITHM
    )

# authenticate(request.args['token'])
def authenticate(auth_token):
    try:
        auth_token = request.args['token']
        if find_user(decode(auth_token)):
            return True
    except:
        return False
    return False

def create_auction(artigoId, precoMinimo, titulo, descricao, data_de_fim):
    try:
        conn = db_connection()
        cur = conn.cursor()

        try:
            if (authenticate(request.args['token'])):
                print()
                username = decode(request.args['token'])
            else:
                return {"error": "Invalid token"}
        except:
            return {"error": "Invalid token"}

        date = datetime.datetime.strptime(data_de_fim, '%m/%d/%Y')
        today = datetime.datetime.now()
        if today > date:
            return {"erro": 'Data incorreta'}  # colocar data default?

        insert = """ INSERT INTO auction (title, description, id, biddding, finish_date, auction_user_username) 
                VALUES (%s, %s, %s, %s, %s, %s)"""
        values = (titulo, descricao, artigoId, precoMinimo, date, username)
        cur.execute(insert, values)

        conn.commit()
        cur.close()
        return {"leilaoId": artigoId}

    except Exception as e:
        return {"erro": '{m}'.format(m=str(e))}

# DB CONNECTION
def db_connection():
    db = psycopg2.connect(**params)
    return db

# MAIN
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



    logger.info(DIV + "API v1.0 online: http://localhost:8080/\n\n")


    app.run(host="0.0.0.0", debug=True, threaded=True)

