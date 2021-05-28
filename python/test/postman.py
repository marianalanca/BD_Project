import requests
from multiprocessing import Process
from threading import Event, Lock, Thread
import json

URL = 'http://localhost:8080'
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

import string
import random

passed_var = 0
fail = 0
total = 0

auths = []
auctions = []

auth_temp = ''

# print(f"{bcolors.WARNING}Warning: No active frommets remain. Continue?{bcolors.ENDC}")

def code_200(request):
    return request.status_code == 200


def contains(request, *name):
    for coisa in name:
        if (coisa not in request.json().keys()):
            return False
    return True


def randomString(size):
    letters = string.ascii_letters
    str_final = str(''.join(random.choice(letters) for i in range(size)))
    return str_final

#TODO CORRECT
def createUser(username, password):
    global auths
    req = requests.post(f'{URL}/user', json={"username": username, "password":password})
    auths.append({"username": username, "password": password})
    return code_200(req) and contains(req, 'userId')


def authenticateUser(username, password):
    global auth_temp
    req = requests.put(f'{URL}/user', json={"username": username, "password":password})
    if (contains(req, 'authToken')):
        auth_temp = req.json()['authToken']
    return code_200(req) and contains(req, 'authToken')


def createAuction(authToken):
    req = requests.put(f'{URL}/leilao?token={authToken}')
    return code_200(req) # and contains(req, 'Create Auctions')


def listAllAuctions(authToken):
    req = requests.get(f'{URL}/leiloes?token={authToken}')
    return code_200(req) and type(req.json()) is list


def searchAuctions():

    random_words = ['cama', 'cana', 'bonita', 'velha', 'pesca', 'antiga', 'teste', 'random', 'word', 'dente', 'nada', 'nenhuma']
    keyword = random.choice(random_words)

    user = random.choice(auths)
    authToken = user['auth']

    req = requests.get(f'{URL}/leiloes/{keyword}?token={authToken}')

    list_dict = req.json()
    if code_200(req) and list_dict is not None:
        if len(list_dict) == 0:
            passed('NO AUCTION WITH KEYWORD ' + keyword + ' FOUND')
        else:
            passed(str(len(list_dict)) + ' AUCTIONS WITH KEYWORD ' + keyword + ' FOUND')
    else:
        failed('SEARCH AUCTION FAILED')


def searchAuctionDetails(auction_id, authToken):
    req = requests.get(f'{URL}/leilao/{auction_id}?token={authToken}')
    return code_200(req) # and contains(req, 'Auction Details')

def activity(authToken):
    req = requests.get(f'{URL}/ativ/?token={authToken}')
    return code_200(req) # and contains(req, 'Activity')

#TODO CORRECT
def bid(auction_id, authToken, bid):
    req = requests.get(f'{URL}/licitar/{auction_id}/{bid}?token={authToken}')
    return code_200(req) and contains(req, 'Status')


def editAuction(auction_id, authToken, bid):
    return


def sendMessage(authToken, auctionID, message):
    req = requests.post(f'{URL}/mural/{auctionID}?token={authToken}', json={"message": message})
    return code_200(req) and contains(req, 'Status')

 
def messageBox(authToken):
    req = requests.get(f'{URL}/messageBox?token={authToken}')
    return code_200(req) and contains(req, 'Message Box')


# MESSAGES


def passed(message):
    print(f"{bcolors.OKGREEN}PASSED: {message}{bcolors.ENDC}")


def failed(message):
    print(f"{bcolors.FAIL}FAILED: {message}{bcolors.ENDC}")


# TESTING


# CREATE USER
def createUsers():
    for _ in range(20):
        user = randomString(5)
        if (createUser(user, randomString(10))):
            passed(f'succeded to create {user}')
        else:
            failed(f'failed to create {user}')


def testCreateUsers():
    users_aux = []
    print('-- CREATE USERS TEST --')

    for _ in range(5):
        q = Thread(target=createUsers)
        q.start()
        users_aux.append(q)
    for p in users_aux:
        p.join()

    print('-- CREATE USERS TEST END --')


# AUTHENTICATE

def testAuthenticateUsersPASS():
    global auths
    print('-- AUTH USERS TEST --')
    for user in auths:
        if authenticateUser(user['username'], user['password']):
            passed(f'succeded to authenticate {user}')
            user['auth'] = auth_temp
        else:
            failed(f'failed to authenticate {user}')

    print('-- AUTH USERS TEST END --')
    return


def testAuthenticateUsersFAIL():
    global auths
    print('-- AUTH USERS TEST FAIL --')
    if not authenticateUser('', 'randomPass'):
        passed(f'succeded to fail test authenticate without username')
    else:
        failed(f'succeded to fail test authenticate without username')


    if not authenticateUser('randomUser', ''):
        passed(f'succeded to fail test authenticate without password')
    else:
        failed(f'succeded to fail test authenticate without password')

    if not authenticateUser('', ''):
        passed(f'succeded to fail test authenticate without credentials')
    else:
        failed(f'succeded to fail test authenticate without credentials')


    if not authenticateUser('debug', 'wrong_pass'):
        passed(f'succeded to fail test authenticate with wrong password')
    else:
        failed(f'succeded to fail test authenticate with wrong password')

    if not authenticateUser('wrong_debug', 'wrong_pass'):
        passed(f'succeded to fail test authenticate with wrong credentials')
    else:
        failed(f'succeded to fail test authenticate with wrong credentials')

    print('-- AUTH USERS TEST FAIL END --')
    return


# BID

def bids():
    global fail
    global total
    global passed_var
    for _ in range(80):
        auction = random.choice(auctions)
        user = random.choice(auths)
        total +=1
        new_bid = random.randint(auction['minimum'], auction['minimum'] + 100)
        if bid(auction['auctionID'], user['auth'], new_bid):
            passed('Succeded to bid ' + auction['auctionID'] + ' ' + user['username'] + ' ' + str(new_bid))
            passed_var += 1
            auction['minimum'] = new_bid + 1
        else:
            failed('Failed to bid ' + auction['auctionID'] + ' ' + user['username'] + ' ' + str(new_bid))
            fail += 1


def testBid():
    global fail
    global total
    global passed_var
    auc = []

    total = fail = passed_var = 0
    
    print('-- BID TEST --')

    for _ in range(20):
        q = Thread(target=bids)
        q.start()
        auc.append(q)
    for p in auc:
        p.join()

    print (f'Passed {passed_var}/{total}; Failed {fail}/{total}')

    print('-- BID TEST END --')


# List Auctions

def listAuctions():
    global fail
    global total
    global passed_var
    for _ in range(20):
        user = random.choice(auths)
        total +=1
        if listAllAuctions( user['auth']):
            passed('Succeded to list all auctions')
            passed_var += 1
        else:
            failed('Failed to list all auctions')
            fail += 1


def testListAuctions():
    global fail
    global total
    global passed_var
    auc = []

    total = fail = passed_var = 0
    
    print('-- LIST AUCTIONS TEST --')

    for _ in range(5):
        q = Thread(target=listAuctions)
        q.start()
        auc.append(q)
    for p in auc:
        p.join()

    print (f'Passed {passed_var}/{total}; Failed {fail}/{total}')

    print('-- LIST AUCTIONS TEST END --')


# SEND MESSAGES

def sendMenssages():
    global fail
    global total
    global passed_var
    for _ in range(20):
        user = random.choice(auths)
        auction = random.choice(auctions)
        total +=1
        if sendMessage(user['auth'], auction['auctionID'], randomString(random.randint(10, 500))):
            passed('Succeded to send message')
            passed_var += 1
        else:
            failed('Failed to send message')
            fail += 1


def testSendMenssages():
    global fail
    global total
    global passed_var
    auc = []

    total = fail = passed_var = 0
    
    print('-- SEND MESSAGES TEST --')

    for _ in range(10):
        q = Thread(target=sendMenssages)
        q.start()
        auc.append(q)
    for p in auc:
        p.join()

    print (f'Passed {passed_var}/{total}; Failed {fail}/{total}')

    print('-- SEND MESSAGES TEST END --')


# MESSAGE BOX  

def listMessages():
    global fail
    global total
    global passed_var
    for _ in range(20):
        user = random.choice(auths)
        total +=1
        if messageBox(user['auth']):
            #passed('Succeded to list all messages from message box')
            passed_var += 1
        else:
            #failed('Failed to list all messages from message box')
            fail += 1


def testListMessages():
    global fail
    global total
    global passed_var
    auc = []

    total = fail = passed_var = 0
    
    print('-- LIST MESSAGES TEST --')

    for _ in range(10):
        q = Thread(target=listMessages)
        q.start()
        auc.append(q)
    for p in auc:
        p.join()

    print (f'Passed {passed_var}/{total}; Failed {fail}/{total}')

    print('-- LIST MESSAGES TEST END --')


# SEARCH AUCTIONS 

def search_auctions():
    global fail
    global total
    global passed_var
    global auths
    auc = []

    print('-- SEARCH AUCTIONS WITH KEYWORD --')
    for _ in range(20):
        q = Thread(target=searchAuctions)
        q.start()
        auc.append(q)
    for p in auc:
        p.join()

    print('-- SEARCH AUCTIONS WITH KEYWORD END --\n')


    print('-- SEARCH AUCTIONS DETAILS --')
    for i in range(10):
        user = random.choice(auths)
        auction = random.choice(auctions)
        if searchAuctionDetails(auction['auctionID'], user['auth']):
            passed('FOUND ' + auction['auctionID'])
        else:
            failed('NOT FOUND' + auction['auctionID'])
if __name__=='__main__':

    with open('users_data.json') as json_file:
        auths = json.load(json_file)

    with open('auctions_data.json') as json_file:
        auctions = json.load(json_file)

    
    print('-- TESTING --')
    try :
        testCreateUsers()
        testAuthenticateUsersPASS()
        testAuthenticateUsersPASS()
        testAuthenticateUsersFAIL()
        testListAuctions()
        testBid()
        testSendMenssages()
        testListMessages()
        
        testSendMenssages()
    except:
        print('Something went wrong')

    with open('users_data.json', 'w') as outfile:
        json.dump(auths, outfile, indent=4)

    with open('auctions_data.json', 'w') as outfile:
        json.dump(auctions, outfile, indent=4)
