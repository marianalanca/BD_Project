import string
import random

code = ''
letters = string.digits
code = ''.join(random.choice(letters) for i in range(13))

print(code)