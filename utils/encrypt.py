from cryptography.fernet import Fernet

key = Fernet.generate_key()
crypto = Fernet(key)

f1 = open('unencrypted.txt', 'r')
f2 = open('encrypted.txt', 'w')
for line in f1:
  f2.write(crypto.encrypt(line[:-1].encode()).decode() + '\n')

print("Please save this key: " + key.decode())
