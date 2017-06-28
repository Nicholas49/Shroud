import convert as con


class User:
    def __init__(self, name, passw, pkeys, salta, saltb):
        self.username = name
        self.hashpass = passw
        self.pkeys = pkeys
        self.salta = salta
        self.saltb = saltb
        self.contactlist = {}

Olys = User("O1ys", con.salt_hash("DefaultPassword", "badsalta"), "fauxpkeys", "badsalta", "badsaltb")
Users = [Olys]
