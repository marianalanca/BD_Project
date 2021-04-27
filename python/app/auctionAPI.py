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
INSERT_USER = """ INSERT INTO auction_user VALUES (%s, %s) RETURNING username """
SELECT_AUCTIONS = " SELECT id, description FROM auction "
SELECT_USERDATA = """ SELECT username, password  FROM auction_user where username=%s"""
SELECT_USER = """ SELECT username  FROM auction_user where username=%s"""
INSERT_AUCTION = """ INSERT INTO auction (title, description, id, biddding, finish_date, auction_user_username) 
                VALUES (%s, %s, %s, %s, %s, %s)"""

# FLASK METHODS

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
    try:
        if (authenticate(request.args['token'])):
            return
        else:
            return {"error": "Invalid authentication"}
    except:
        return {"error": "Invalid authentication"}

# TODO TEST
@app.route('/leiloes' , methods=['GET'])
def leiloes():
    try:
        if (authenticate(request.args['token'])):
            try:
                conn = db_connection()
                cur = conn.cursor()
                cur.execute(SELECT_AUCTIONS)
                auctionsDB = cur.fetchall()
                conn.commit()
                cur.close()
                if auctionsDB == None:
                    return jsonify([])
                # passar para json
                auctions = []
                for auction in auctionsDB:
                    auctions.append({"leilaoId": auction[0], "descricao": auction[1]})

                return jsonify(auctions)
            except:
                return {"error":"Something went wrong"}
        else:
            return {"error": "Invalid authentication"}
    except:
        return {"error": "Invalid authentication"}

@app.route('/licitar/<leilaoId>/<licitacao>', methods=['GET'])
def licitar(leilaoId, licitacao):
    try:
        if (authenticate(request.args['token'])):
            return bid(leilaoId, licitacao, decode(request.args['token']))
        else:
            return {"error": "Invalid authentication"}
    except:
        return {"error": "Invalid authentication"}

# TODO
@app.route('/messageBox', methods=['GET'])
def message():
    try:
        if (authenticate(request.args['token'])):
            return
        else:
            return {"error": "Invalid authentication"}
    except:
        return {"error": "Invalid authentication"}


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

# FUNCTIONALITIES

def insert_auction_user(username, password):
    try :
        conn = db_connection()
        # create a cursor
        cur = conn.cursor()
        cur.execute(INSERT_USER, (username, password,))
        new_id = cur.fetchone()[0]
        conn.commit()
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

        values = (titulo, descricao, artigoId, precoMinimo, date, username)
        cur.execute(INSERT_AUCTION, values)

        conn.commit()
        cur.close()
        return {"leilaoId": artigoId}

    except Exception as e:
        return {"erro": '{m}'.format(m=str(e))}

# TODO FINISH
def bid(auctionID, bidValue, username):
    try:
        conn = db_connection()
        cur = conn.cursor()

        select_auction = """ SELECT bidding, finish_date FROM auction where id=%s"""

        cur.execute(select_auction, (auctionID,))

        auction = cur.fetchall()

        if auction == None:
            logger.error('Auction ID does not exist')
            return {"erro": 'Auction ID does not exist'}

        # TODO adicionar parte de adicionar biding à lista de bids

        bid_date = datetime.datetime.now()
        # logger.info(bid_date)
        '''try:
            if bid_date > auction[0][1]: # and
                logger.error('The auction has already closed')
                return {"error": "The auction has already closed"}
        except:
            logger.error('Could not convert date to right format')
            return {"error": "Could not convert date to right format"}
        '''

        try:
            if int(bidValue) <= int(auction[0][0]):
                logger.error('Bid value is too low')
                return {"error": "Bid value is too low"}
        except:
            logger.error('Could not convert price to int')
            return {"erro": 'Could not convert price to int'}

        select_auction = """ UPDATE auction SET bidding=%s WHERE id=%s"""
        cur.execute(select_auction, (bidValue, auctionID,))

        # HERE

        insert_bidding = """ INSERT INTO bidding VALUES (%s, %s) WHERE id=%s"""

        # ! DÁ ERRO
        #cur.execute(insert_bidding, (bidValue, bid_date, auctionID,))

        conn.commit()
        logger.info('Successful bid')
        return {"Status": "Successful bid"}
    except Exception as e:
        return {"erro": '{m}'.format(m=str(e))}
    finally:
        cur.close()

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



    logger.info(DIV + "API v1.0 online: http://localhost:8080/\n")


    app.run(host="0.0.0.0", debug=True, threaded=True)

