import requests
from multiprocessing import Process

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


'''
def func1():
  print 'func1: starting'
  for i in xrange(10000000): pass
  print 'func1: finishing'

def func2():
  print 'func2: starting'
  for i in xrange(10000000): pass
  print 'func2: finishing'

if __name__ == '__main__':
  p1 = Process(target=func1)
  p1.start()
  p2 = Process(target=func2)
  p2.start()
  p1.join()
  p2.join()
'''


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


def searchAuctionDetails(auction_id, authToken, bid):
    return


def bid(auction_id, authToken, bid):
    return


def editAuction(auction_id, authToken, bid):
    return


def sendMessage(authToken, message, auctionID):
    req = requests.post(f'{URL}/mural/{auctionID}?token={authToken}')
    return code_200(req) and contains(req, 'Message Box')


def messageBox(authToken):
    req = requests.get(f'{URL}/messageBox?token={authToken}')
    return code_200(req) and contains(req, 'Status')


def passed(message):
    print(f"{bcolors.OKGREEN}PASSED: {message}{bcolors.ENDC}")


def failed(message):
    print(f"{bcolors.FAIL}FAILED: {message}{bcolors.ENDC}")


if __name__=='__main__':
    print('-- TESTING --')
    
    print('-- CREATE USERS --')
    for i in range(10):
        if (createUser(randomString(5), randomString(10))):
            passed('')
        else:
            failed('')
