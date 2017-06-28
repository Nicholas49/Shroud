import uuid as uu
import alphabets as alf
import convert as con
import pcrypt as pcr
import data
import retrieve as ret


def start_menu():
    ret.populate_user_list()

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
                theuser = ret.finduser(signupresult['username'])
                main_program(theuser, signupresult['hashbass'])

        elif choice == "2":
            signinresult = signin()
            if not signinresult == "bad":
                theuser = ret.finduser(signinresult['username'])
                main_program(theuser, signinresult['hashbass'])

        elif choice == "3":
            break

        else:
            badinput("3")


def signup():
    # Asks user for username and password. If both check out it generates a random public/private key pair then
    # 2 random salts for encryption and encrypts the pkeys using the password and a salt
    # it then finishes up by writing this all to a new line in the users.txt file and generates an empty user_contacts
    # file.

    # Ask for username and verify that it hasn't already been taken.

    username = input("Enter Username: ")

    if ret.verifyuser(username):
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

    salta = uu.uuid4().hex
    saltb = uu.uuid4().hex
    hashworda = con.salt_hash(password, salta)
    hashwordb = con.salt_hash(password, saltb)

    # Generate pkeys (public and private keys, plus the modulus), then convert them to a string
    #  and encrypt using the password and saltb

    keys = pcr.gen_pkeys()
    pkeystring = str(keys[0]) + "l" + str(keys[1]) + "l" + str(keys[2])
    hexedpkeys = con.base(pkeystring, alf.hexsplit, alf.hexd)
    encrypted_pkeys = con.encrypt(hexedpkeys, hashwordb, hashwordb)

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

    newuser = data.User(username, hashworda, encrypted_pkeys, salta, saltb)
    data.Users.append(newuser)
    print("Account Created")
    br(4)

    # Lastly, return the username and password so the main program can use them

    return {'username': username, 'hashbass': hashwordb}


def signin():

    # Ask for username and verify that it doesn't match the username of any existing user objects

    username = input("Enter Username: ")

    if ret.finduser(username):
        theuser = ret.finduser(username)
    else:
        print("User not found")
        return "bad"

    # Ask for password, hash it, then compare the hash to the hashpass for the retrieved user object
    # if the hashed passwords match, return the username and password as a dictionary
    # otherwise, offer users the options to re-enter the password or go back to the main menu

    while True:

        password = input("Enter Password: ")

        hashworda = con.salt_hash(password, theuser.salta)
        hashwordb = con.salt_hash(password, theuser.saltb)

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
        ret.populate_contact_list(youser, hashbass)

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

        themedium = con.base(themessage)
        nonce = uu.uuid4().hex
    else:

        # Apologies for the McLuhan reference

        themedium = themessage.split("l")[0]
        nonce = themessage.split("l")[1]

    # Finally the message in ready to be encrypted or decrypted using the crypt() function

    encrypted_message = con.crypt(themedium, youser.contactlist[contact_names[snumb]], nonce, en)

    if en:
        encrypted_message += "l" + nonce
        print("Encrypting...")
    else:
        encrypted_message = con.base(encrypted_message, alf.hexd, alf.full)
        print("Decrypting...")

    print("Complete.")
    print("Here it is: ")
    br()
    print(encrypted_message)
    input("")
    br(2)


def add_contact(userguy, hashbass):
    pkeys = con.base(con.decrypt(userguy.pkeys, hashbass, hashbass), alf.hexd, alf.hexsplit)
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

        contname = ""
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

            cipher = uu.uuid4().hex
            int_ciph = con.toint(cipher, alf.hexd)

            miniciph = int_ciph % fmodulus
            finalciph = con.tostring(miniciph, alf.hexd)

            print("Encrypting... this might take a while on slow computers.")
            enc_ciph = con.pcrypt(fmodulus, int(fpubkey[1]), miniciph)

            print("Encryption complete!")
            print("Send " + contname + " this encrypted cipher: " + str(enc_ciph))
            ret.importciph(userguy, contname, finalciph, hashbass)
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
            cyph = con.tostring(con.pcrypt(modulus, privkey, ecyph), alf.hexd)
            print("Cipher successfully decrypted!")

            ret.importciph(userguy, contname, cyph, hashbass)
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


start_menu()
