# POSTGRESQL & PSYCOPG2
# https://www.postgresqltutorial.com/postgresql-python/
# https://www.postgresql.org/docs/9.2/sql-insert.html
# https://www.psycopg.org/docs/usage.html

# FLASK
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
INSERT_AUCTION = """ INSERT INTO auction (title, description, id, bidding, finish_date, final_user_username, auction_user_username)
                VALUES (%s, %s, %s, %s, %s, %s, %s)"""


# TODO ORGANIZAR
# * TRIGGER:
#   Quando se faz uma bid, acciona 2 triggers: um para alterar o valor do bid e outro para adicionar a mensagem a dizer que o valor de bid foi alterado
#   Ter outro para quando acaba? -> adicionar winner ao
# * Script para correr vários requests ao mesmo tempo


@app.route('/user', methods=['POST', 'PUT'])
def user():
    req = request.get_json()
    if request.get_json() is None and len(req) == 2 and ('username' in req.keys()) and ('password' in req.keys()):
        if request.method == 'POST':
            return insertAuctionUser(**req)
        else:
            return autenticationAuctionUser(**req)  # fazer verificação
    logger.error(f'{DIV}Wrong Arguments\n')
    return {"erro": "Wrong arguments"}


@app.route('/leilao', methods=['POST'])
def leilao():
    args = request.get_json()
    if args != None and len(args) == 5:
        return createAuction(**args)
    return {"erro": "Wrong number of arguments"}


@app.route('/ativ/', methods=['GET'])
def ativ():
    try:
        if authenticate(request.args['token']):
            return activity_auction(decode(request.args['token']))
        else:
            return {"error": "Invalid authentication"}
    except:
        return {"error": "Invalid authentication"}


# TODO
@app.route('/leilao/<leilaoId>', methods=['GET', 'PUT'])
def leilaoId(leilaoId):
    try:
        if (authenticate(request.args['token'])):
            if request.method == 'GET':
                return consult_auction(leilaoId)
            else:  # PUT
                return changeDetails(leilaoId, request.get_json())
        else:
            return {"error": "Invalid authentication"}
    except:
        return {"error": "Invalid authentication"}


@app.route('/leiloes/<keyword>', methods=['GET', 'PUT'])
def leiloesK(keyword):
    try:
        if authenticate(request.args['token']):
            if request.method == 'GET':
                return search_auctions(keyword)
            else:
                return change_auction(keyword)
        else:
            return {"error": "Invalid authentication"}
    except:
        return {"error": "Invalid authentication"}


# TODO TEST
@app.route('/leiloes', methods=['GET'])
def leiloes():
    try:
        # TODO passar para uma função
        if (authenticate(request.args['token'])):
            try:
                conn = db_connection()
                conn.set_session(readonly=True)
                cur = conn.cursor()
                cur.execute(SELECT_AUCTIONS)
                auctionsDB = cur.fetchall()
                conn.commit()
                cur.close()
                if auctionsDB == None:
                    return jsonify([])
                auctions = []
                for auction in auctionsDB:
                    auctions.append({"leilaoId": auction[0], "descricao": auction[1]}) # TODO Aparece ao contrário

                return jsonify(auctions)
            except:
                return {"error": "Something went wrong"}
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


@app.route('/mural/<leilaoId>', methods=['POST'])
def sendMural(leilaoId):
    try:
        if (authenticate(request.args['token'])):
            message = request.get_json()['message']
            return sendMessageMural(message, leilaoId, decode(request.args['token']))
        else:
            return {"error": "Invalid authentication"}
    except Exception as e:
        return {"error": '{m}'.format(m=str(e))}


@app.route('/messageBox', methods=['GET'])
def message():
    try:
        if (authenticate(request.args['token'])):
            return messageBox(decode(request.args['token']))
        else:
            return {"error": "Invalid authentication"}
    except:
        return {"error": "Invalid authentication"}


def match_password(username, password):
    conn = db_connection()
    conn.set_session(readonly=True)
    cur = conn.cursor()
    cur.execute(SELECT_USERDATA, (username,))
    try:
        if password != decode(cur.fetchone()[1]):
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
        conn.set_session(readonly=True)
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
    # 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=90),
    payload = {
        'iat': datetime.datetime.utcnow(),
        'sub': value
    }
    return jwt.encode(
        payload,
        JWT_SECRET,
        algorithm=JWT_ALGORITHM
    )


def authenticate(auth_token):
    try:
        auth_token = request.args['token']
        if find_user(decode(auth_token)):
            return True
    except:
        return False
    return False


# FUNCTIONALITIES

def insertAuctionUser(username, password):
    try:
        conn = db_connection()
        # create a cursor
        cur = conn.cursor()
        if (validString(username)):
            passw = encode(password)
            logger.info(passw)
            logger.info(len(passw))
            cur.execute(INSERT_USER, (username, passw,))
            new_id = cur.fetchone()[0]
            conn.commit()
            logger.info(f'{DIV}User {new_id} created successfuly\n')
            return {"userId": new_id}
        error_message = 'Username cannot contain special characters'
        logger.error(f'{DIV}{error_message}\n')
        return {"erro": error_message}
    except Exception as e:
        error = '{m}'.format(m=str(e))
        logger.error(f'{DIV}{error}\n')
        return {"erro": error}
    finally:
        cur.close()


def autenticationAuctionUser(username, password):
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


def createAuction(artigoId, precoMinimo, titulo, descricao, data_de_fim):
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

        date = datetime.datetime.strptime(data_de_fim, '%d/%m/%Y, %H:%M')  # dia/mes/ano, hora:minuto
        today = datetime.datetime.now()
        if today > date:
            return {"erro": 'Data incorreta'}  # colocar data default?

        values = (titulo, descricao, artigoId, precoMinimo, date, None, username)
        cur.execute(INSERT_AUCTION, values)

        conn.commit()
        cur.close()
        return {"leilaoId": artigoId}

    except Exception as e:
        return {"erro": '{m}'.format(m=str(e))}


# TODO ver se não tem outras coisas
# se tiver argumento duplicado só aceita o segundo
# ignora tudo o que esteja fora do title e descirption
# * TRIGGER?
def changeDetails(leilaoId, definitions):
    if len(definitions) != 0:
        try:
            conn = db_connection()
            cur = conn.cursor()

            select_auction = """ SELECT title, description FROM auction where id=%s"""
            cur.execute(select_auction, (leilaoId,))
            old_data = cur.fetchall()[0]

            change_date = datetime.datetime.now()
            insert_history = """ INSERT INTO history VALUES (%s, %s, %s, %s) """
            cur.execute(insert_history, (change_date, old_data[0], old_data[1], leilaoId))

            title = old_data[0]
            description = old_data[1]

            if 'title' in definitions.keys():
                update_titulo = """ UPDATE auction SET title=%s WHERE id=%s"""
                cur.execute(update_titulo, (definitions['title'], leilaoId,))
                title = definitions['title']
            if 'description' in definitions.keys():
                update_titulo = """ UPDATE auction SET description=%s WHERE id=%s"""
                cur.execute(update_titulo, (definitions['description'], leilaoId,))
                description = definitions['description']

            if title == old_data[0] and description == old_data[1]:
                conn.rollback()
                logger.error(f'{DIV}Nothing has changed\n')
                return {"error": "Nothing has changed"}

            conn.commit()
            return {"leilaoId": leilaoId, "title": title, "description": description}
        except Exception as e:
            error = '{m}'.format(m=str(e))
            logger.error(f'{DIV}{error}\n')
            return {"error": error}
        finally:
            cur.close()
    else:
        logger.error(f'{DIV}Lack of arguments\n')
        return {"error": "Lack of arguments"}


def search_auctions(keyword):
    try:
        conn = db_connection()
        conn.set_session(readonly=True)
        cur = conn.cursor()

        command = f"""SELECT id, description FROM auction WHERE id LIKE '%{keyword}%' or description LIKE '%{keyword}%'"""
        cur.execute(command)

        result = cur.fetchall()

        if result is not None:
            return jsonify([{"leilaoId": x[0], "descricao": x[1]} for x in result])
        else:
            return {"error": 'not found'}

    except Exception as e:
        return {"erro": '{m}'.format(m=str(e))}


def change_auction(keyword):
    return {"fazer": "editar"}


def consult_auction(leilaoId):
    try:
        conn = db_connection()
        conn.set_session(readonly=True)
        cur = conn.cursor()

        command = f"""SELECT * FROM auction WHERE id = '{leilaoId}' """
        cur.execute(command)

        result = cur.fetchall()

        if result is not None:
            # INCOMPLETO - falta as mensagens e o historico (secalhar nem precisa destes detalhes todos - disuctir isto)
            dict_result = {"leilaoId": result[0][2], "titulo": result[0][0], "descricao": result[0][1],
                           "data": result[0][3], "licitacao": result[0][4], "vendedor": result[0][5]}
            return jsonify(dict_result)
        else:
            return {"error": 'not found'}

    except Exception as e:
        return {"erro": '{m}'.format(m=str(e))}


def activity_auction(username):
    try:
        conn = db_connection()
        conn.set_session(readonly=True)
        cur = conn.cursor()

        # INCOMPLETO
        # OR  (SELECT id_auction FROM bidding WHERE auction_user_username = '{username}')
        command = f"""SELECT id, title, description FROM auction WHERE auction_user_username = '{username}'"""
        cur.execute(command)

        result = cur.fetchall()

        if result is not None:
            return jsonify([{"leilaoId": x[0], "title": x[1], "descricao": x[2]} for x in result])
        else:
            return {"error": 'not found'}

    except Exception as e:
        return {"erro": '{m}'.format(m=str(e))}


def validString(str):
    return not any(not c.isalnum() for c in str)


def bid(auctionID, bidValue, username):
    try:
        conn = db_connection()
        cur = conn.cursor()

        select_auction = """ SELECT bidding, finish_date FROM auction where id=%s"""
        cur.execute(select_auction, (auctionID,))
        auction = cur.fetchone()

        if auction is None:
            logger.error(f'{DIV}Auction ID does not exist')
            return {"erro": 'Auction ID does not exist'}

        bid_date = datetime.datetime.now()
        date = auction[0][1]
        logger.info(f'{type(bid_date)} {bid_date} {date}')

        try:
            if bid_date > date:
                logger.error('The auction has already closed')
                return {"error": "The auction has already closed"}
        except:
            logger.error(f'{DIV}Could not convert date to right format ')
            return {"error": "Could not convert date to right format"}

        try:
            if int(bidValue) <= int(auction[0][0]):
                logger.error('Bid value is too low')
                return {"error": "Bid value is too low"}
        except:
            logger.error('Could not convert price to int')
            return {"erro": 'Could not convert price to int'}

        # update bidding value in auction
        select_auction = """ UPDATE auction SET bidding=%s, final_user_username=%s WHERE id=%s"""
        cur.execute(select_auction, (bidValue, username, auctionID,))

        # Insert into bidding table
        insert_bidding = """ INSERT INTO bidding VALUES (%s, %s, %s, %s)"""
        cur.execute(insert_bidding, (bidValue, bid_date, auctionID, username))

        conn.commit()
        logger.info(f'{DIV}Successful bid')
        return {"Status": "Successful bid"}

    except Exception as e:
        error = '{m}'.format(m=str(e))
        logger.error(f'{DIV}{error}')
        return {"erro": error}

    finally:
        cur.close()


def sendMessageMural(message, auction_ID, user):
    try:
        conn = db_connection()
        cur = conn.cursor()

        msg_time = datetime.datetime.now()

        insert_message = """ INSERT INTO mural_msg VALUES(%s, %s, %s, %s, %s); """ 

        for receiver in getSenders(auction_ID, cur):
            cur.execute(insert_message, (f"{receiver}_{auction_ID}_{msg_time}", message, msg_time, auction_ID, receiver))

        conn.commit()
        logger.info(f'{DIV}Message sent successfully')
        return {"Status": "Message sent successfully"}
    except Exception as e:
        error = '{m}'.format(m=str(e))
        logger.error(f'{DIV}{error}')
        return {"erro": error}
    finally:
        cur.close()


# TODO TEST
def getAuctionWinner(auctionID):
    try:
        conn = db_connection()
        cur = conn.cursor()

        select_auction = """SELECT  finish_date, final_user_username FROM auction where auction_id=%s"""
        cur.execute(select_auction, (auctionID,))
        possible_winner = cur.fetchone()

        if possible_winner is None:
            logger.error(f'{DIV}Auction ID does not exist')
            return {"erro": 'Auction ID does not exist'}

        try:

            atual_date = datetime.datetime.now()
            date = possible_winner[0][0]
            # logger.info(f'{type(atual_date)} {atual_date} {date}')

            if atual_date < date:
                logger.error('The auction is still opened, there is no winner')
                return {"error": "The auction is still opened, there is no winner"}
            else:
                winner = possible_winner[0][1]

                if winner is None:
                    logger.error('There is no winner')
                    return {"error": "There is no winner"}

                return {"Status": winner}

        except:
            logger.error(f'{DIV}Could not convert date to right format ')
            return {"error": "Could not convert date to right format"}

    finally:
        cur.close()


def messageBox(user):
    try:
        conn = db_connection()
        conn.set_session(readonly=True)
        cur = conn.cursor()

        select_message = """ SELECT content, sent_date FROM mural_msg WHERE auction_user_username=%s """ 

        cur.execute(select_message, (user,))

        res = cur.fetchall()
        
        conn.commit()
        logger.info(f'{DIV}{res}')
        return jsonify(res)
    except Exception as e:
        error = '{m}'.format(m=str(e))
        logger.error(f'{DIV}{error}')
        return {"erro": error}
    finally:
        cur.close()


def getSenders(auction_ID, cur):
    select_receivers = f""" SELECT auction_user_username from auction where id='{auction_ID}' UNION select auction_user_username from bidding where auction_id='{auction_ID}' UNION select auction_user_username from mural_msg where auction_id='{auction_ID}'; """ 
    cur.execute(select_receivers)
    return [r[0] for r in cur.fetchall()]


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
