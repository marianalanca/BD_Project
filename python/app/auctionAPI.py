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


@app.route('/user', methods=['POST', 'PUT'])
def user():
    req = request.get_json()
    if contains(request, 2, 'username', 'password'):
        if request.method == 'POST':
            return insertAuctionUser(**req)
        else:
            return autenticationAuctionUser(**req)  # fazer verificação
    logger.error(f'{DIV}Wrong Arguments\n')
    return {"error": "Wrong arguments"}


@app.route('/leilao', methods=['POST'])
def leilao():
    args = request.get_json()
    if contains(request, 5, 'artigoId', 'precoMinimo', 'titulo' , 'descricao', 'data_de_fim'):
        return createAuction(**args)
    return {"error": "Wrong arguments"}


@app.route('/ativ/', methods=['GET'])
def ativ():
    try:
        if authenticate(request.args['token']):
            return activity_auction(decode(request.args['token']))
        else:
            return {"error": "Invalid authentication"}
    except:
        return {"error": "Invalid authentication"}


@app.route('/leilao/<leilaoId>', methods=['GET', 'PUT'])
def leilaoId(leilaoId):
    try:
        if (authenticate(request.args['token'])):
            if request.method == 'GET':
                return consult_auction(leilaoId)
            else:  # PUT
                if contains(request, 1, 'title') or contains(request, 1, 'description') or contains(request, 2, 'title', 'description'):
                    return changeDetails(leilaoId, request.get_json(), decode(request.args['token']))
                else:
                    return {"error": "Invalid arguments"}
        else:
            return {"error": "Invalid authentication"}
    except:
        return {"error": "Invalid authentication"}


@app.route('/leiloes/<keyword>', methods=['GET'])
def leiloesK(keyword):
    try:
        if authenticate(request.args['token']):
            if request.method == 'GET':
                return search_auctions(keyword)
        else:
            return {"error": "Invalid authentication"}
    except:
        return {"error": "Invalid authentication"}


@app.route('/leiloes', methods=['GET'])
def leiloes():
    try:
        if (authenticate(request.args['token'])):
            return listAllAuctions()
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
        if authenticate(request.args['token']):
            if contains(request, 1, 'message'):
                message = request.get_json()['message']
                return sendMessageMural(message, leilaoId, decode(request.args['token']), True)
            else: 
                return {"error": "Wrong arguments"}
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


@app.route('/history/<auctionID>', methods=['GET'])
def historyEndpoint(auctionID):
    try:
        if (authenticate(request.args['token'])):
            return consultHistory(auctionID)
        else:
            return {"error": "Invalid authentication"}
    except:
        return {"error": "Invalid authentication"}


@app.route('/finish', methods=['GET'])
def finishEndpoint():
    try:
        if (authenticate(request.args['token'])):
            return finish()
        else:
            return {"error": "Invalid authentication"}
    except:
        return {"error": "Invalid authentication"}


def match_password(username, password):
    conn = db_connection()
    conn.set_session(readonly=True)
    cur = conn.cursor()

    select_userdata = """ SELECT username, password  FROM auction_user where username=%s"""

    cur.execute(select_userdata, (username,))
    try:
        fetched = cur.fetchone()
        if password != decode(fetched[1]):
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

        select_userdata = """ SELECT username, password  FROM auction_user where username=%s"""
        cur.execute(select_userdata, (username,))
        return jsonify(cur.fetchone()[1])
    except:
        return {}
    finally:
        cur.close()


def decode(encoded):
    return jwt.decode(encoded, JWT_SECRET, JWT_ALGORITHM)['sub']


def encode(value):
    payload = {
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
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


def contains(request, expected_params_num, *parameters):
    body = request.get_json()
    if body is not None and len(body) != expected_params_num:
        return False
    for parameter in parameters:
        if parameter not in body.keys():
            return False
    return True


# FUNCTIONALITIES


def insertAuctionUser(username, password):
    try:
        conn = db_connection()
        # create a cursor
        cur = conn.cursor()
        if (validString(username)):
            payload = {
                'iat': datetime.datetime.utcnow(),
                'sub': password
            }
            passw =  jwt.encode(
                payload,
                JWT_SECRET,
                algorithm=JWT_ALGORITHM
            )
            
            insert_user = """ INSERT INTO auction_user VALUES (%s, %s) RETURNING username """

            cur.execute(insert_user, (username, passw,))
            fetched = cur.fetchone()
            if fetched is None or len(fetched)==0:
                logger.error(f'{DIV}Something went wrong.\n')
                return {"error": "Something went wrong."}

            new_id = fetched[0]
            conn.commit()
            logger.info(f'{DIV}User {new_id} created successfuly\n')
            return {"userId": new_id}
        error_message = 'Username cannot contain special characters'
        logger.error(f'{DIV}{error_message}\n')
        return {"error": error_message}
    except Exception as e:
        error = '{m}'.format(m=str(e))
        logger.error(f'{DIV}{error}\n')
        return {"error": error}
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
        return {"error": error}


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
            return {"error": 'Data incorreta'}  # colocar data default?

        values = (titulo, descricao, artigoId, precoMinimo, date, None, username)

        inser_auction = """ INSERT INTO auction (title, description, id, bidding, finish_date, final_user_username, auction_user_username) VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        cur.execute(inser_auction, values)

        conn.commit()
        cur.close()
        return {"leilaoId": artigoId}

    except Exception as e:
        return {"error": '{m}'.format(m=str(e))}


def changeDetails(leilaoId, definitions, user):
    if len(definitions) != 0:
        try:
            conn = db_connection()
            cur = conn.cursor()

            # fazer select da pessoa que fez a auction

            select_auction = """ SELECT title, description, auction_user_username FROM auction where id=%s"""
            cur.execute(select_auction, (leilaoId,))
            fetched = cur.fetchall()

            if fetched is None or len(fetched)==0:
                logger.info(f'{DIV}Auction {leilaoId} does not exist\n')
                return {"error": f"Auction {leilaoId} does not exist"}

            old_data = fetched[0]

            logger.info(f'{DIV}{old_data}\n')

            creator = old_data[2]

            logger.info(f'{DIV}{creator} {user}\n')

            if creator != user : 
                logger.info(f'{DIV}<{user}> does not have permission to change auction details\n')
                return {"error": f"<{user}> does not have permission to change auction details"}

            title = old_data[0]
            description = old_data[1]

            if 'title' in definitions.keys():
                title = definitions['title']
            if 'description' in definitions.keys():
                description = definitions['description']

            if title == old_data[0] and description == old_data[1]:
                conn.rollback()
                logger.error(f'{DIV}Nothing has changed\n')
                return {"error": "Nothing has changed"} 

            update_auction = """ UPDATE auction set title=%s, description=%s where id=%s"""
            cur.execute(update_auction, (title, description, leilaoId,))

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


def consultHistory(auctionId):
    try:
        history_register = []

        conn = db_connection()
        conn.set_session(readonly=True)
        cur = conn.cursor()

        select_history = """ SELECT change_date, old_title, old_description FROM history where auction_id=%s"""
        cur.execute(select_history, (auctionId,))
        fetched = cur.fetchall()

        if fetched is None or len(fetched)==0:
            logger.info(f'{DIV}There were no modifications done to auction {auctionId}\n')
            return {"error": f"There were no modifications done to auction {auctionId}"}

        for _ in fetched:
            change_date = fetched[0][0]
            old_title = fetched[0][1]
            old_description = fetched[0][1]
            history_register.append({"Title":old_title, "old_description": old_description, "updated": change_date})

        conn.commit()
        return jsonify(history_register)

    except Exception as e:
        error = '{m}'.format(m=str(e))
        logger.error(f'{DIV}{error}\n')
        return {"error": error}
    finally:
        cur.close()



def search_auctions(keyword):
    try:
        conn = db_connection()
        conn.set_session(readonly=True)
        cur = conn.cursor()

        command = f"""SELECT id, description FROM auction WHERE id LIKE '%{keyword}%' or description LIKE '%{keyword}%'"""
        cur.execute(command)

        result = cur.fetchall()

        if result is not None and len(result) > 0:
            return jsonify([{"leilaoId": x[0], "descricao": x[1]} for x in result])
        else:
            return {"error": 'not found'}

    except Exception as e:
        return {"error": '{m}'.format(m=str(e))}


def consult_auction(leilaoId):
    try:
        conn = db_connection()
        conn.set_session(readonly=True)
        cur = conn.cursor()

        command = f"""SELECT * FROM auction WHERE id = '{leilaoId}' """
        cur.execute(command)

        result = cur.fetchall()

        if result is not None and len(result) > 0:

            command = f"""SELECT DISTINCT content FROM mural_msg WHERE auction_id = '{leilaoId}' """
            cur.execute(command)

            messages = cur.fetchall()

            command = f"""SELECT  price, bid_date, auction_user_username FROM bidding WHERE auction_id = '{leilaoId}' """
            cur.execute(command)

            biddings = cur.fetchall()

            dict_result = {"leilaoId": result[0][2], "titulo": result[0][0], "descricao": result[0][1],
                           "data": result[0][3], "licitacao": result[0][4], "vencedor": result[0][5], "vendedor": result[0][6],
                           "mensagens": messages, "licitacoes": biddings}
            return jsonify(dict_result)
        else:
            return {"error": 'not found'}

    except Exception as e:
        return {"error": '{m}'.format(m=str(e))}


def activity_auction(username):
    try:
        conn = db_connection()
        conn.set_session(readonly=True)
        cur = conn.cursor()

        command = f"""SELECT id, title, description FROM auction WHERE auction_user_username = '{username}'"""
        cur.execute(command)

        result = cur.fetchall()

        command = f"""SELECT DISTINCT id, title, description FROM auction JOIN bidding on id=auction_id WHERE bidding.auction_user_username = '{username}'"""
        cur.execute(command)

        aux = cur.fetchall()
        set1 = set(result)
        set2 = set(aux)
        set_aux = list(set2 - set1)
        result.extend(set_aux)

        command = f"""SELECT DISTINCT auction.id, title, description FROM auction JOIN mural_msg ON auction.id=auction_id WHERE mural_msg.auction_user_username = '{username}'"""
        cur.execute(command)

        aux = cur.fetchall()
        set1 = set(result)
        set2 = set(aux)
        set_aux = list(set2 - set1)
        result.extend(set_aux)

        if result is not None and len(result) > 0 :
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
        auction = cur.fetchall()

        if auction is None or len(auction) == 0:
            logger.error(f'{DIV}Auction ID does not exist')
            return {"error": 'Auction ID does not exist'}

        bid_date = datetime.datetime.now()
        date = auction[0][1]
        
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
            return {"error": 'Could not convert price to int'}

        # update bidding value in auction
        select_auction = """ UPDATE auction SET bidding=%s WHERE id=%s"""
        cur.execute(select_auction, (bidValue, auctionID,))

        # Insert into bidding table
        insert_bidding = """ INSERT INTO bidding VALUES (%s, %s, %s, %s)"""
        cur.execute(insert_bidding, (bidValue, bid_date, auctionID, username))

        conn.commit()
        logger.info(f'{DIV}Successful bid')
        return {"Status": "Successful bid"}

    except Exception as e:
        error = '{m}'.format(m=str(e))
        logger.error(f'{DIV}{error}')
        return {"error": error}

    finally:
        cur.close()


def sendMessageMural(message, auction_ID, user, op):
    try:
        conn = db_connection()
        cur = conn.cursor()

        msg_time = datetime.datetime.now()

        insert_message = """ INSERT INTO mural_msg VALUES(%s, %s, %s, %s, %s); """ 

        cur.execute(insert_message, (f"{user}_{auction_ID}_{msg_time}", message, msg_time, auction_ID, user))

        if op:
            for receiver in getSenders(auction_ID, cur):
                if receiver!=user:
                    cur.execute(insert_message, (f"{receiver}_{auction_ID}_{msg_time}", message, msg_time, auction_ID, receiver))

        conn.commit()
        logger.info(f'{DIV}Message sent successfully')
        return {"Status": "Message sent successfully"}
    except Exception as e:
        error = '{m}'.format(m=str(e))
        logger.error(f'{DIV}{error}')
        return {"error": error}
    finally:
        cur.close()


def messageBox(user):
    try:
        conn = db_connection()
        conn.set_session(readonly=True)
        cur = conn.cursor()

        select_message = """ SELECT content, sent_date, auction_id FROM mural_msg WHERE auction_user_username=%s """ 

        cur.execute(select_message, (user,))

        fetched = cur.fetchall()

        messages = []
        for message in fetched:
            messages.append({"Content": message[0], "Date": message[1], "Auction": message[2]})

        conn.commit()
        logger.info(f'{DIV}{messages}')
        return jsonify({'Message Box': messages})
    except Exception as e:
        error = '{m}'.format(m=str(e))
        logger.error(f'{DIV}{error}')
        return {"error": error}
    finally:
        cur.close()


def getSenders(auction_ID, cur):
    select_receivers = f""" SELECT auction_user_username from auction where id='{auction_ID}' UNION select auction_user_username from bidding where auction_id='{auction_ID}' UNION select auction_user_username from mural_msg where auction_id='{auction_ID}'; """ 
    cur.execute(select_receivers)
    return [r[0] for r in cur.fetchall()]


def listAllAuctions():
    try:
        conn = db_connection()
        conn.set_session(readonly=True)
        cur = conn.cursor()

        select_auctions = """ SELECT id, description FROM auction WHERE finish_date > now() """

        cur.execute(select_auctions)
        auctionsDB = cur.fetchall()
        conn.commit()
        cur.close()
        if auctionsDB == None or len(auctionsDB) == 0:
            return jsonify([])
        auctions = []
        for auction in auctionsDB:
            auctions.append({"leilaoId": auction[0], "descricao": auction[1]}) # TODO Aparece ao contrário

        return jsonify(auctions)
    except:
        return {"error": "Something went wrong"}


def finish():

    try:
        conn = db_connection()
        cur = conn.cursor()

        select_auctions = """ SELECT FOR UPDATE id, auction_user_username, bidding FROM auction WHERE final_user_username IS NULL AND finish_date < now() """
        cur.execute(select_auctions)

        result = cur.fetchall()

        logger.info(f'{DIV}{result}')

        for i in result:
            id_auction = i[0]
            seller = i[1]
            bidding = i[2]

            command = f"""SELECT auction_user_username FROM bidding WHERE price = '{bidding}' AND auction_id = '{id_auction}'"""
            cur.execute(command)

            user = cur.fetchone()
            logger.info(f'{DIV}{user}')
            if user is None:
                sendMessageMural(f'The {id_auction} auctions has finished but there is no winner', id_auction, seller, False)
            else:
                user = user[0]

                logger.info(f'{DIV}{user}')

                # update do final_user_username
                update_winner = f"""UPDATE auction SET final_user_username='{user}' WHERE id='{id_auction}'"""
                cur.execute(update_winner)

                
                logger.info(f'{DIV}{seller}')

                # mensagens
                sendMessageMural(f'The {id_auction} auctions has finished. You are the winner!', id_auction, user, False)
                sendMessageMural(f'The {id_auction} auctions has finished. The winner is {user}', id_auction, seller, False)
        
        conn.commit()
        logger.info(f'{DIV}Status: Updated with success ')
        return jsonify({"Status": "Updated with success"})
        
        
    except Exception as e:
        error = '{m}'.format(m=str(e))
        logger.error(f'{DIV}{error}')
        return {"error": error}

    # buscar todas as auctions que têm winner null
    # e que já terminaram
    # envia mensagem
    # descobre o winner e faz update
    return


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
