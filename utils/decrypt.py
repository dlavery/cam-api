import sys
from cryptography.fernet import Fernet

key = sys.argv[1].encode()
crypto = Fernet(key)

f1 = open('encrypted.txt', 'r')
f2 = open('decrypted.txt', 'w')
for line in f1:
  f2.write(crypto.decrypt(line[:-1].encode()).decode() + '\n')
