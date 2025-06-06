import bcrypt

# Change this to the password you want to hash 1.ewpass@2015 Strong@123
plain = "Strong@123".encode('utf-8')
hashed = bcrypt.hashpw(plain, bcrypt.gensalt())
print(hashed.decode())
