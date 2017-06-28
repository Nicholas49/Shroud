import uuid as uu
import alphabets as alf
import data
import convert as con


def populate_user_list():

    # Opens the users.txt file and converts each line of data into a User object, then adds this to the Users list"""

    filey = open("users.txt", "r")

    for liney in filey:
        userdata = liney.split()
        thisuser = data.User(userdata[0], userdata[1], userdata[2], userdata[3], userdata[4])
        data.Users.append(thisuser)


def populate_contact_list(user, hashbass):

    filer = open("user_contacts/" + user.username + "_contacts.txt", "r")
    for ln in filer:
        linesp = ln.split("l")
        c_inf = linesp[0]
        c_salt = linesp[1]
        if len(c_inf) > 1:
            dehashed_contact = con.base(con.decrypt(c_inf, hashbass, c_salt), alf.hexd, alf.full)
            splitcontact = dehashed_contact.split("%")
            user.contactlist[splitcontact[0]] = splitcontact[1]


def importciph(youser, contactname, cipher, hashbass):

    contactsalt = uu.uuid4().hex

    contactfilename = "user_contacts/" + youser.username + "_contacts.txt"
    filez = open(contactfilename, "a")
    filez.write(con.encrypt(con.base(contactname+"%"+cipher), hashbass, contactsalt)+"l"+contactsalt + "l" + "\n")
    filez.close()


def verifyuser(usersearch):
    for u in data.Users:
        if u.username == usersearch:
            return True
    return False


def finduser(usersearch):
    # Searches through the User objects and returns the one who's username matches the provided string

    for u in data.Users:
        if u.username == usersearch:
            return u
