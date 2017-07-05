import uuid as uu
import alphabets as alf
import convert as con
import pcrypt as pcr
import data
import retrieve as ret
import ui


# This file is the main body of the program, and is where the program actually runs.
# The smaller functions and objects that support this one have been sorted and moved into the 'ui', 'retrieve', 'data',
# 'pcrypt', 'convert', and 'alphabets' .py files


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
            ui.badinput("3")


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
            if ui.goback():
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
    ui.br(4)

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
            if ui.goback():
                return "bad"


def main_program(youser, hashbass):

    # All contact data is retrieved, a lengthy process but it's included in the while loop so that if new contacts are
    # added, the user doesn't have to log out and back in to use them.

    while True:
        ret.populate_contact_list(youser, hashbass)

        # A straitforward menu. If none of the available options are picked the user is prompted retry until one is

        ui.br(2)
        print("-- Main Menu --")
        ui.br(2)
        print("Pick an Operation: ")
        print("1: Encrypt")
        print("2: Decrypt")
        print("3: Manage Contacts")
        print("4: Logout")
        ui.br()
        op = input("> ")

        if op == "1":
            cryptmenu(youser, True)
        elif op == "2":
            cryptmenu(youser, False)
        elif op == "3":

            while True:
                print("1: Add Contact")
                print("2: Delete Contact")
                print("3: Print Contact/Cipher List")
                print("4: Return")
                ui.br()

                op2 = input("> ")

                if op2 == "1":
                    add_contact(youser, hashbass)

                elif op2 == "2":
                    print("Which contact do you want to delete?")
                    ui.br()

                    contact = ui.choose_contact(youser)
                    if not contact:
                        ui.br()
                    else:
                        youser.contactlist.remove(contact)
                        ret.savecontacts(youser, hashbass)

                        print("Deleted " + contact['name'] + " from contact list.")
                        ui.continu()

                elif op2 == "3":

                    ui.br(2)
                    print("Your Contacts: ")
                    ui.br(2)
                    for cn in youser.contactlist:
                        print("Name: " + cn['name'])
                        print("Cipher: " + cn['cipher'])
                        ui.br()
                    input("")
                    ui.br(2)
                elif op2 == "4":
                    break
                else:
                    ui.badinput("4")
        elif op == "4":
            return
        else:
            ui.badinput("5")


def cryptmenu(youser, en):

    # This function is multipurpose, it either encrypts or decrypts based on the second value passed in
    # Retrieve the keys (names) of all the contacts and print them out for the user to select

    contact = ui.choose_contact(youser)

    if not contact:
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

    encrypted_message = con.crypt(themedium, contact['cipher'], nonce, en)

    if en:
        encrypted_message += "l" + nonce
        print("Encrypting...")
    else:
        encrypted_message = con.base(encrypted_message, alf.hexd, alf.full)
        print("Decrypting...")

    print("Complete.")
    print("Here it is: ")
    ui.br()
    print(encrypted_message)
    input("")
    ui.br(2)


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
        ui.br()
        choise = input("> ")

        contname = ""
        if choise == "1":
            print("Send this Public Key: " + str(modulus) + "l" + str(pubkey))
            input("")
            break
        elif choise == "2":

            while True:
                contname = input("Enter the name of the contact: ")
                if ret.oldcontact(contname, userguy):
                    if ui.goback():
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
            ui.br(2)
            break
        elif choise == "3":

            while True:
                contname = input("Enter the name of the contact: ")
                if ret.oldcontact(contname, userguy):
                    if ui.goback():
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
            ui.br(2)
            break
        elif choise == "4":
            break
        else:
            ui.badinput("4")


start_menu()
