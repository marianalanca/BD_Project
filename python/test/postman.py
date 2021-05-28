import requests
from multiprocessing import Process
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
    return ''.join(random.choice(letters) for i in range(size))

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


def createAuction(auction_id, authToken, bid):
    return

#TODO 
def listAuctions(auction_id, authToken, bid):
    req = requests.get(f'{URL}/leiloes?token={authToken}')
    return code_200(req)# and contains(req, 'Status')
    # test if array


def searchAuctions(auction_id, authToken, bid):
    return


def searchAuctionDetails(auction_id, authToken, bid):
    return

#TODO 
def bid(auction_id, authToken, bid):
    req = requests.get(f'{URL}/licitar/{auction_id}/{bid}?token={authToken}')
    return code_200(req) and contains(req, 'Status')


def editAuction(auction_id, authToken, bid):
    return

#TODO 
def sendMessage(authToken, message, auctionID):
    req = requests.post(f'{URL}/mural/{auctionID}?token={authToken}')
    return code_200(req) and contains(req, 'Message Box')

#TODO 
def messageBox(authToken):
    req = requests.get(f'{URL}/messageBox?token={authToken}')
    return code_200(req) and contains(req, 'Status')


# MESSAGES


def passed(message):
    print(f"{bcolors.OKGREEN}PASSED: {message}{bcolors.ENDC}")


def failed(message):
    print(f"{bcolors.FAIL}FAILED: {message}{bcolors.ENDC}")


# TESTING


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
        q = Process(target=createUsers)
        q.start()
        users_aux.append(q)
    for p in users_aux:
        p.join()

    print('-- CREATE USERS TEST END --')


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


def bids():
    for _ in range(20):
        auction = random.choice(auctions)
        user = random.choice(auths)
        new_bid = random.randint(auction['minimum'], auction['minimum'] + 100)
        if bid(auction['auctionID'], user['auth'], new_bid):
            passed('Succeded to bid ' + auction['auctionID'] + ' ' + user['username'] + ' ' + str(new_bid))
            auction['minimum'] = new_bid + 1
        else:
            failed('Failed to bid ' + auction['auctionID'] + ' ' + user['username'] + ' ' + str(new_bid))




if __name__=='__main__':

    with open('users_data.json') as json_file:
        auths = json.load(json_file)

    with open('auctions_data.json') as json_file:
        auctions = json.load(json_file)

    
    print('-- TESTING --')

    # testCreateUsers()
    # testAuthenticateUsersPASS()
    # testAuthenticateUsersFAIL()

    bids()

    # print(auths)

    # no final guarda os users
    with open('users_data.json', 'w') as outfile:
        json.dump(auths, outfile, indent=4)

    with open('auctions_data.json', 'w') as outfile:
        json.dump(auctions, outfile, indent=4)
