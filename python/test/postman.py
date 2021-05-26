import requests

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


# print(f"{bcolors.WARNING}Warning: No active frommets remain. Continue?{bcolors.ENDC}")

def code_200(request):
    return request.status_code == 200

# TEST
def contains(request, *name):
    for coisa in name:
        if (coisa not in request.json().keys()):
            return False
    return True

def randomString(size):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(size))

def createUser(username, password):
    req = requests.post(f'{URL}/user', json={"username": username, "password":password})
    return code_200(req) and contains(req, 'userId')

def authenticateUser(username, password):
    req = requests.put(f'{URL}/user', json={"username": username, "password":password})
    return code_200(req) and contains(req, 'authToken')


def createAuction(auction_id, authToken, bid):
    return


def listAuctions(auction_id, authToken, bid):
    return

def searchAuctions(auction_id, authToken, bid):
    return


def searchAuction(auction_id, authToken, bid):
    return


def bid(auction_id, authToken, bid):
    return


def editAuction(auction_id, authToken, bid):
    return


def sendMessage():
    return


def messageBox():
    return


if __name__=='__main__':
    print('-- TESTING --')
    for i in range(10):
        if (createUser(randomString(5), randomString(10))):
            print(f"{bcolors.OKGREEN}PASSED{bcolors.ENDC}")
        else:
            print(f"{bcolors.FAIL}FAILED{bcolors.ENDC}")
