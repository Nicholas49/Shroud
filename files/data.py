import convert as con

# The User object is where all the significant data about each user is stored for easy access throughout the program.
# The objects are initialized as soon as the program starts and all the variables are written except the contactlist
# which must first be decrypted using the user's password


class User:
    def __init__(self, name, passw, pkeys, salta, saltb):
        self.username = name
        self.hashpass = passw
        self.pkeys = pkeys
        self.salta = salta
        self.saltb = saltb
        self.contactlist = []

Olys = User("O1ys", con.salt_hash("DefaultPassword", "badsalta"), "fauxpkeys", "badsalta", "badsaltb")
Users = [Olys]
