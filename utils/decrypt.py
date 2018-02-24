import sys
from cryptography.fernet import Fernet

if len(sys.argv) < 2:
    print('please supply a decryption key')
    exit(0)

key = sys.argv[1].encode()
crypto = Fernet(key)

f1 = open('encrypted.csv', 'r')
f2 = open('decrypted.csv', 'w')
for line in f1:
    if line[-1] == '\n':
        line = line[:-1]
    f2.write(crypto.decrypt(line.encode()).decode() + '\n')
