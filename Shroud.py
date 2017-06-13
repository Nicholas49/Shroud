import hashlib
import uuid
import random
import math

fullalf = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ ',./=-;<>?+_:!@#$%^&*()[]{}`~|"

hexalf = "0123456789abcdef"

hexalfsplit = hexalf + "l"


class User:
    def __init__(self, name, passw, pkeys, salta, saltb):
        self.username = name
        self.hashpass = passw
        self.pkeys = pkeys
        self.salta = salta
        self.saltb = saltb
        self.contactlist = {}


# Main Interface


def start_menu():
    populate_user_list()

    while True:
        print("1: Sign Up")
        print("2: Sign In")
        print("3: Exit")
        choice = input("> ")

    # When the user selects the operation to perform their userdata is either generated or retrieved, either way their
    # username and (hashed) password is passed into the main program.

        if choice == "1":
            signupresult = signup()
            if not signupresult == "bad":
                theuser = finduser(signupresult['username'])
                main_program(theuser, signupresult['hashbass'])

        elif choice == "2":
            signinresult = signin()
            if not signinresult == "bad":
                theuser = finduser(signinresult['username'])
                main_program(theuser, signinresult['hashbass'])

        elif choice == "3":
            break

        else:
            badinput("3")


def signup():
    """Asks user for username and password. If both check out it generates a random public/private key pair then
    2 random salts for encryption and encrypts the pkeys using the password and a salt
    it then finishes up by writing this all to a new line in the users.txt file and generates an empty user_contacts
    file."""

    # Ask for username and verify that it hasn't already been taken.

    username = input("Enter Username: ")

    if verifyuser(username):
        print("Username already exists. Please use another.")
        return "bad"

    # Ask for a password and verify that it's 12 characters or more before continuing
    password = ""
    while True:
        password = input("Enter Password: ")

        if len(password) < 12:
            print("Password must be greater than 12 characters.")
            if goback():
                return "bad"
        else:
            break

    # Generate salts and use one to hash the password

    salta = uuid.uuid4().hex
    saltb = uuid.uuid4().hex
    hashworda = salt_hash(password, salta)
    hashwordb = salt_hash(password, saltb)

    # Generate pkeys (public and private keys, plus the modulus), then convert them to a string
    #  and encrypt using the password and saltb

    keys = gen_pkeys()
    pkeystring = str(keys[0]) + "l" + str(keys[1]) + "l" + str(keys[2])
    hexedpkeys = base_convert(pkeystring, hexalfsplit, hexalf)
    encrypted_pkeys = crypt(hexedpkeys, hashwordb, hashwordb)

    # Write all the input and generated data into a new line in the users.txt file

    filey = open("users.txt", "a")
    filey.write(username + " " + hashworda + " " + encrypted_pkeys + " " + salta + " " + saltb + "\n")
    filey.close()

    # Create a username_contacts file for the user, but leave it blank for now

    newcontactsfile = "user_contacts/" + username + "_contacts.txt"
    filez = open(newcontactsfile, "a")
    filez.close()

    # Create a user object with all the data and add it to the users list, since this new user didn't exist when we
    # called the populate_user_list() function earlier

    newuser = User(username, hashworda, encrypted_pkeys, salta, saltb)
    Users.append(newuser)
    print("Account Created")
    br(4)

    # Lastly, return the username and password so the main program can use them

    return {'username': username, 'hashbass': hashwordb}


def signin():

    # Ask for username and verify that it doesn't match the username of any existing user objects

    username = input("Enter Username: ")

    if finduser(username):
        theuser = finduser(username)
    else:
        print("User not found")
        return "bad"

    # Ask for password, hash it, then compare the hash to the hashpass for the retrieved user object
    # if the hashed passwords match, return the username and password as a dictionary
    # otherwise, offer users the options to re-enter the password or go back to the main menu

    while True:

        password = input("Enter Password: ")

        hashworda = salt_hash(password, theuser.salta)
        hashwordb = salt_hash(password, theuser.saltb)

        if hashworda == theuser.hashpass:
            print("Successful Login")
            return {'username': username, 'hashbass': hashwordb}
        else:
            print("Wrong password")
            if goback():
                return "bad"


def main_program(youser, hashbass):

    # All contact data is retrieved, a lengthy process but it's included in the while loop so that if new contacts are
    # added, the user doesn't have to log out and back in to use them.

    while True:
        populate_contact_list(youser, hashbass)

        # A straitforward menu. If none of the available options are picked the user is prompted retry until one is

        br(2)
        print("-- Main Menu --")
        br(2)
        print("Pick an Operation: ")
        print("1: Encrypt")
        print("2: Decrypt")
        print("3: Add Contact")
        print("4: Print Contact List")
        print("5: Logout")
        br()
        op = input("> ")

        if op == "1":
            cryptmenu(youser, True)
        elif op == "2":
            cryptmenu(youser, False)
        elif op == "3":
            add_contact(youser, hashbass)
        elif op == "4":

            # The only operation performed inside the main program instead of being referenced from outside because
            # it's so short. Very helpful for debugging, but I left it in so users can keep track of their contacts.

            br(2)
            print("Your contacts: ")
            contact_names = list(youser.contactlist.keys())
            for cn in contact_names:
                print(cn)
                print(youser.contactlist[cn])
            br(2)
        elif op == "5":
            return
        else:
            badinput("5")


def cryptmenu(youser, en):

    # This function is multipurpose, it either encrypts or decrypts based on the second value passed in
    # Retrieve the keys (names) of all the contacts and print them out for the user to select

    contact_names = list(youser.contactlist.keys())
    snumb = 1

    while True:
        print("Select Contact")
        br()

        num = 1
        for cname in contact_names:
            print(str(num) + ": " + cname)
            num += 1

        selection = input("> ")
        snumb = int(selection) - 1

        if 0 <= snumb < len(contact_names):
            break
        else:
            badinput(str(len(contact_names)))
            if goback():
                return

    print("Enter message:")
    themessage = input("> ")

    if en:

        # Converts the message to hexidecimal since the crypt function only works with
        # A nonce is packaged with the message to avoid reusing the same cipher each time which would make the
        # cipher vulnerable

        themedium = base_convert(themessage)
        nonce = uuid.uuid4().hex
    else:

        # Apologies for the McLuhan reference

        themedium = themessage.split("l")[0]
        nonce = themessage.split("l")[1]

    # Finally the message in ready to be encrypted or decrypted using the crypt() function

    encrypted_message = crypt(themedium, youser.contactlist[contact_names[snumb]], nonce, en)

    if en:
        encrypted_message += "l" + nonce
        print("Encrypting...")
    else:
        encrypted_message = base_convert(encrypted_message, hexalf, fullalf)
        print("Decrypting...")

    print("Complete.")
    print("Here it is: ")
    br()
    print(encrypted_message)
    input("")
    br(2)


def add_contact(userguy, hashbass):
    pkeys = base_convert(crypt(userguy.pkeys, hashbass, hashbass, False), hexalf, hexalfsplit)
    pkeylist = pkeys.split("l")
    modulus = int(pkeylist[0])
    pubkey = int(pkeylist[1])
    privkey = int(pkeylist[2])

    while True:
        print("Are you creating or importing a contact?")
        print("")
        print("1: Send public key")
        print("2: Send encrypted cipher")
        print("3: Import encrypted cipher")
        print("4: Return")
        br()
        choise = input("> ")

        if choise == "1":
            print("Send this Public Key: " + str(modulus) + "l" + str(pubkey))
            input("")
            break
        elif choise == "2":

            while True:
                contname = input("Enter the name of the contact: ")
                if oldcontact(contname, userguy):
                    if goback():
                        return
                else:
                    break

            fpubkey = input("Enter Public Key: ").split("l")
            fmodulus = int(fpubkey[0])

            cipher = uuid.uuid4().hex
            int_ciph = toint(cipher, hexalf)

            miniciph = int_ciph % fmodulus
            finalciph = tostring(miniciph, hexalf)

            print("Encrypting... this might take a while on slow computers.")
            enc_ciph = pcrypt(fmodulus, int(fpubkey[1]), miniciph)

            print("Encryption complete!")
            print("Send " + contname + " this encrypted cipher: " + str(enc_ciph))
            importciph(userguy, contname, finalciph, hashbass)
            input("")
            br(2)
            break
        elif choise == "3":

            while True:
                contname = input("Enter the name of the contact: ")
                if oldcontact(contname, userguy):
                    if goback():
                        return
                else:
                    break

            ecyph = int(input("Enter " + contname + "'s encrypted cipher: "))

            print("Decrypting cipher... ")
            cyph = tostring(pcrypt(modulus, privkey, ecyph), hexalf)
            print("Cipher successfully decrypted!")

            importciph(userguy, contname, cyph, hashbass)
            print("Cipher imported")
            print("You may now communicate with " + contname + " securely.")

            input("")
            br(2)
            break
        elif choise == "4":
            break
        else:
            badinput("4")


def oldcontact(contname, user):
    prior_contacts = list(user.contactlist.keys())
    for pc in prior_contacts:
        if contname == pc:
            print("A contact with that name already exists.")
            return True
    return False


def badinput(num):
    print("Not a valid entry.")
    if num == "2":
        print("Enter 1 or 2.")
    else:
        print("Enter a number (1 - " + num + ")")


def goback():
    while True:
        print("")
        print("1: Try again")
        print("2: Return")
        choice = input("> ")
        if choice == "1":
            return False
        elif choice == "2":
            return True
        badinput("2")


def br(numb=1):
    numb = int(numb)
    for i in range(numb):
        print("")


# Data Retrieval

def populate_user_list():
    # Opens the users.txt file and converts each line of data into a User object, then adds this to the Users list"""

    filey = open("users.txt", "r")

    for liney in filey:
        userdata = liney.split()
        thisuser = User(userdata[0], userdata[1], userdata[2], userdata[3], userdata[4])
        Users.append(thisuser)


def populate_contact_list(user, hashbass):

    filer = open("user_contacts/" + user.username + "_contacts.txt", "r")
    for ln in filer:
        linesp = ln.split("l")
        c_inf = linesp[0]
        c_salt = linesp[1]
        if len(c_inf) > 1:
            dehashed_contact = base_convert(crypt(c_inf, hashbass, c_salt, False), hexalf, fullalf)
            splitcontact = dehashed_contact.split("%")
            user.contactlist[splitcontact[0]] = splitcontact[1]


def importciph(youser, contactname, cipher, hashbass):

    contactsalt = uuid.uuid4().hex

    contactfilename = "user_contacts/" + youser.username + "_contacts.txt"
    filez = open(contactfilename, "a")
    filez.write(crypt(base_convert(contactname + "%" + cipher), hashbass, contactsalt) + "l" + contactsalt + "l" + "\n")
    filez.close()


def verifyuser(usersearch):
    for u in Users:
        if u.username == usersearch:
            return True
    return False


def finduser(usersearch):
    # Searches through the User objects and returns the one who's username matches the provided string

    for u in Users:
        if u.username == usersearch:
            return u


# Conversion

def base_convert(text,
                 alfin="0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ ',./=-;<>?+_:!@#$%^&*()[]{}`~|",
                 alfout="0123456789abcdef"):
    return tostring(toint(text, alfin), alfout)


def crypt(hext, hexkey, salt="none", en=True):

    # The salt is optional, but usually used since it allows for unique ciphers
    # If a salt is present it gets hashed with the key to create a new key unrecognizable from the original
    # but still fully deterministic."""

    # This is the core function the program is built around. It's a multipurpose function that can encrypt or
    # decrypt based on the first value passed in"""

    hexalph = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "a", "b", "c", "d", "e", "f"]

    # The salt is optional, but usually used since it allows for unique ciphers
    # If a salt is present it gets hashed with the key to create a new key unrecognizable from the original
    # but still fully deterministic."""

    if not salt == "none":
        hexkey = salt_hash(hexkey, salt)

    # In the likely case that the message is longer than the key, the key must be extended to be at least the same
    # length without repeating. Repeating the cipher creates a vulnerability in long messages where letter frequency
    # can be used.
    # I decided to use a block cipher for simplicity's sake. Each block segment is the hash of the previous
    # making the whole thing predictable based on the original key, but non-repeating.

    bloqq = hash_alg(hexkey)
    while len(hext) > len(hexkey):
        hexkey += bloqq
        bloqq = hash_alg(bloqq)

    # Both the message and the cipher are converted to a list of ints to be added or subtracted

    numbtext = tonumblist(hext, hexalph)
    numbkey = tonumblist(hexkey, hexalph)
    resultnumbs = []
    finaltext = ""

    # We add or subtract the lists entity by entity, values that go above 15 or below zero wrap around

    for b in range(len(numbtext)):
        if en:
            numb = numbtext[b] + numbkey[b % len(numbkey)]
        else:
            numb = len(hexalph) + numbtext[b] - numbkey[b % len(numbkey)]
        resultnumbs.append(numb)

    # And we convert the result into a string to return

    for b in resultnumbs:
        finaltext += hexalph[b % len(hexalph)]

    return finaltext


def pcrypt(n, key, message):
    encrypted = pow(message, key, n)
    return encrypted


def toint(stri, alf):

    # takes in a string of characters and then, using the supplied alphabet, interprets the
    # string as a number with a base the size of the alphabet, each character representing a digit.
    # It then converts this number to a base 10 representation and returns it as an integer."""

    numblist = tonumblist(stri, alf)

    total = 0

    alflen = len(alf)
    count = len(numblist) - 1
    for numb in numblist:
        total += int(numb) * (alflen ** count)
        count -= 1

    return total


def tostring(numb, alf):
    # The inverse of toint, this function takes in an integer and converts it into a
    # a 'base x' representation in the form of a string where x is the number of
    # characters in the provided alphabet"""

    count = 0
    outstring = ""

    alflen = len(alf)

    while numb >= (alflen ** count):
        count += 1
    count -= 1

    while count >= 0:
        powr = alflen ** count
        digi = math.floor(numb / powr)
        outstring += alf[digi]
        numb %= powr
        count -= 1

    return outstring


def tonumblist(text, alf3):
    # Converts a string of characters into a list of integers based on their position in the supplied alphabet

    numbi = []

    for x in text:
        for y in range(len(alf3)):
            if x == alf3[y]:
                numbi.append(y)

    return numbi


def salt_hash(pas, salt):
    return hashlib.sha256(salt.encode() + pas.encode()).hexdigest()


def hash_alg(pas):
    return hashlib.sha256(pas.encode()).hexdigest()


# Public/Private Key


def gen_pkeys():

    # Uses all the other Public/Private Key functions to generate a working public private key pair using the RSA system

    # First generate two different primes.
    # For now I'm only using numbers up to 10^8 since going larger causes bugs for some reason
    # I fully intend to use much larger primes once I figure out why this is happening

    p = genprime(50, (10 ** 8))
    q = p
    while q == p:
        q = genprime(50, (10 ** 8))
    n = q * p

    # Computing the totient of the two primes

    l = int(lcm(q - 1, p - 1))

    # For the exponent I'm using 17
    # Though if 17 happens to be a divisor of the totient it counts up by 2 until it finds another prime that isn't

    e = 17
    while l % e == 0:
        e += 2
        while not isprime(e):
            e += 2

    # Here I use that scary modular multiplicative inverse function to find the decrypting exponent

    d = multi_inverse(e, l)

    # And return it all as a list for easy accessability

    return [n, e, int(d)]


def isprime(numb):

    # fairly straitforward primality test. Saves time by only testing for divisors up to the square root of the number

    if numb % 2 == 0:
        return False
    else:
        for n in range(3, math.ceil(math.sqrt(numb)) + 1, 2):
            if numb % n == 0:
                return False

        return True


def genprime(floor, ceil):

    # Finds a prime number within the provided range using basic trial and error
    # The use of the randint() function is one potential vulnerability of this program since it's not considered
    # Cryptographically secure. I'm looking into replacing it with a better RNG soon.

    if ceil < 11:
        ceil = 11

    p = 12

    while not isprime(p):
        p = random.randint(floor, ceil)

    return p


def lcm(q, p):

    # Uses the greatest common divisor function to efficiently compute the least common multiple

    return (q * p) / gcd(q, p)


def gcd(a, b):

    # Uses Euclids algorithm to compute the greatest common denominator

    while not b == 0:
        temp = b
        b = a % b
        a = temp
    return a


def multi_inverse(a, b):

    # Computes the modular multiplicative inverse of an exponent and modulus using Euclid's Extended Algorithm
    # I'm not gonna lie, I don't really understand the math behind this
    # I'll try to understand it better when I get some time, but for now it's enough to know that it does work

    x = 0
    y = 1
    lx = 1
    ly = 0
    oa = a
    ob = b
    while b != 0:
        q = a // b
        (a, b) = (b, a % b)
        (x, lx) = ((lx - (q * x)), x)
        (y, ly) = ((ly - (q * y)), y)
    if lx < 0:
        lx += ob
    if ly < 0:
        ly += oa

    return lx


# User Class Implementation

Olys = User("O1ys", salt_hash("DefaultPassword", "badsalta"), "fauxpkeys", "badsalta", "badsaltb")
Users = [Olys]

start_menu()
