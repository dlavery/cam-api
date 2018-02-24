from cryptography.fernet import Fernet

key = Fernet.generate_key()
crypto = Fernet(key)

f1 = open('to-be-encrypted.csv', 'r')
f2 = open('encrypted.csv', 'w')
for line in f1:
    if line[-1] == '\n':
        line = line[:-1]
    f2.write(crypto.encrypt(line.encode()).decode() + '\n')

print("encryption-key:" + key.decode())
