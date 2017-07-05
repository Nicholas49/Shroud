import uuid as uu
import alphabets as alf
import data
import convert


# These are all functions that retrieve, or check the existence of, some data stored elsewhere either in the user object
# or the .txt files that longterm info is stored in


def populate_user_list():

    # Opens the users.txt file and converts each line of data into a User object, then adds this to the Users list

    filey = open("users.txt", "r")

    for liney in filey:
        userdata = liney.split()
        thisuser = data.User(userdata[0], userdata[1], userdata[2], userdata[3], userdata[4])
        data.Users.append(thisuser)


def populate_contact_list(user, hashbass):

    # Clears the initial contact list if it isn't already, then reads in each line from the user_contacts.txt
    # file and converts them to dictionaries and appends the contact list with each one
    # This way if any contacts have been added OR deleted it will be reflected in the user object

    user.contactlist = []

    # Reads in the lines and seperates the salt from the rest of the data, which is still encrypted

    filer = open("user_contacts/" + user.username + "_contacts.txt", "r")
    for ln in filer:
        linesp = ln.split("l")
        c_inf = linesp[0]
        c_salt = linesp[1]

    # Uses the passed in hashbass and the salt to decrypt the contact info and converts it from hexidecimal
    # to plaintext

        if len(c_inf) > 1:
            dehashed_contact = convert.base(convert.decrypt(c_inf, hashbass, c_salt), alf.hexd, alf.full)

    # Seperates the contact's name and cipher, and creates a dictionary for the name, cipher, and the salt

            splitcontact = dehashed_contact.split("%")
            contact = {'name': splitcontact[0], 'cipher': splitcontact[1], 'salt': c_salt}
            user.contactlist.append(contact)


def importciph(youser, contactname, cipher, hashbass):

    # This was the function that originally wrote newly added contacts to the user_contacts.txt file.
    # That functionality has since been moved to the 'savecontacts()' function.
    # But this fuction's still used to generate the contact's salt, create the dictionary, and append it to
    # The user_contacts list

    contactsalt = uu.uuid4().hex

    newcont = {'name': contactname, 'cipher': cipher, 'salt': contactsalt}
    youser.contactlist.append(newcont)

    savecontacts(youser, hashbass)


def savecontacts(youser, hashbass):

    # Writes the users current contact list to the user_contacts.txt file in order to save any recent changes
    # Such as a contact being added or deleted

    filez = open("user_contacts/"+youser.username+"_contacts.txt", "w")
    for cn in youser.contactlist:
        linez = cn['name'] + "%" + cn['cipher']
        hexline = convert.base(linez)
        cryptline = convert.encrypt(hexline, hashbass, cn['salt'])
        finline = cryptline + "l" + cn['salt'] + "l\n"
        filez.write(finline)
    filez.close()


def verifyuser(usersearch):

    # Checks to make sure a user actually exists within the Users[] list

    for u in data.Users:
        if u.username == usersearch:
            return True
    return False


def finduser(usersearch):
    # Searches through the User objects and returns the one who's username matches the provided string

    for u in data.Users:
        if u.username == usersearch:
            return u


def oldcontact(contname, user):
    # Checks whether a given name matches the name of any prior contacts in the users contact list
    # Used to avoid doubles

    for pc in user.contactlist:
        if contname == pc['name']:
            print("A contact with that name already exists.")
            return True
    return False
