import uuid as uu

import alphabets as alf
import convert as con
import pcrypt as pcr
import retrieve as ret
import data
import tkinter as tk

# This file is the main body of the program, and is where the program actually runs.
# The smaller functions and objects that support this one have been sorted and moved into the 'ui', 'retrieve', 'data',
# 'pcrypt', 'convert', and 'alphabets' .py files


def signup():
    # Asks user for username and password. If both check out it generates a random public/private key pair then
    # 2 random salts for encryption and encrypts the pkeys using the password and a salt
    # it then finishes up by writing this all to a new line in the users.txt file and generates an empty user_contacts
    # file.

    # Ask for username and verify that it hasn't already been taken.

    username = namebox.get()
    password = passbox.get()
    error = False

    error_mess = ''
    error_label['text'] = ''

    if ret.verifyuser(username):
        error_mess = "Username already exists, please use another"
        error = True

    if len(password) < 12:
        if error:
            error_mess += "\n and \n"
        error_mess += "Password must be over 12 characters"
        error = True

    if error:
        error_label['text'] = error_mess
    else:
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


def signin():

    # Ask for username and verify that it doesn't match the username of any existing user objects

    username = namebox.get()
    password = passbox.get()

    error_label['text'] = ''

    if ret.verifyuser(username):
        theuser = ret.finduser(username)

        hashworda = con.salt_hash(password, theuser.salta)
        hashwordb = con.salt_hash(password, theuser.saltb)

        if hashworda == theuser.hashpass:
            error_mess = ''
            main_program(theuser, hashwordb)
        else:
            error_mess = 'Wrong password'
    else:
        error_mess = 'User not found'

    error_label['text'] = error_mess


def main_program(u, hb):

    fr1.grid_remove()

# All contact data is retrieved, a lengthy process but it's included in the while loop so that if new contacts are
# added, the user doesn't have to log out and back in to use them.

    ret.populate_contact_list(u, hb)

    w = "White"
    b = "Black"
    t = True
    f = False

    menubar = tk.Menu(fr)
    menubar.add_command(label="Logout", command=lambda: logout(framez, fr1))
    menubar.add_command(label="Crypto", command=lambda: menu_swap(framez, fr3))

    contactmenu = tk.Menu(menubar, tearoff=0)
    contactmenu.add_command(label="Delete Contact", command=lambda: menu_swap(framez, frd))
    contactmenu.add_command(label="View Info", command=lambda: menu_swap(framez, fri))

    contactmenu2 = tk.Menu(contactmenu, tearoff=0)
    contactmenu2.add_command(label="Send Cipher", command=lambda: menu_swap(framez, fra))
    contactmenu2.add_command(label="Import Cipher", command=lambda: menu_swap(framez, frm))

    contactmenu.add_cascade(label="Add Contact", menu=contactmenu2)

    menubar.add_cascade(label="Contacts", menu=contactmenu)

    fr3 = tk.Frame(fr, bg=b)

    mess = tk.Entry(fr, bg=b, fg=w, relief=tk.FLAT)
    mess.insert(tk.INSERT, "")
    mess.grid(row=1, column=0)

# Home Menu
# Contact dropdown list
    lstl = ["Self"]

    for c in u.contactlist:
        lstl.append(c['name'])

    varp = tk.StringVar()
    varp.set("select")
    drop = tk.OptionMenu(fr3, varp, *lstl)
    drop.grid(row=1, column=0)

    tx = tk.Text(fr3, relief=tk.FLAT, width=25, height=2)
    tx.grid(row=0, column=0, columnspan=3, pady=6)

# encrypt button
    eb = tk.Button(fr3, text="Encrypt", bg=w, relief=tk.FLAT, command=lambda: cwrap(u, tx, varp.get(), t, hb, mess))
    eb.grid(row=1, column=1, sticky=tk.N)
# decrypt button
    db = tk.Button(fr3, text="Decrypt", bg=w, relief=tk.FLAT, command=lambda: cwrap(u, tx, varp.get(), f, hb, mess))
    db.grid(row=1, column=2, sticky=tk.N)

# send Cipher Menu
    fra = tk.Frame(fr, bg="Black", bd=2)

    namelab = tk.Label(fra, text="Name: ", bg=b, fg=w)
    cname = tk.Entry(fra, relief=tk.FLAT)
    pblab = tk.Label(fra, text="Public Key: ", bg=b, fg=w)
    pbkey = tk.Entry(fra, relief=tk.FLAT)
    q = "Encrypt Cipher"
    sciphr = tk.Button(fra, relief=tk.FLAT, bg=w, text=q, command=lambda: mkc(u, pbkey.get(), cname.get(), hb, mess))

    namelab.grid(row=0, column=0, sticky=tk.E)
    cname.grid(row=0, column=1)
    pblab.grid(row=1, column=0, sticky=tk.E)
    pbkey.grid(row=1, column=1)
    sciphr.grid(row=2, column=0, columnspan=2, pady=5)

# Import Cipher Menu
    frm = tk.Frame(fr, bg=b)

    namelab2 = tk.Label(frm, text="Name: ", bg=b, fg=w)
    cname2 = tk.Entry(frm, relief=tk.FLAT)
    pblab2 = tk.Label(frm, text="Encrypted Cipher: ", bg=b, fg=w)
    pbkey2 = tk.Entry(frm, relief=tk.FLAT)
    x = "Import Cipher"
    sciphr = tk.Button(frm, relief=tk.FLAT, bg=w, text=x, command=lambda: imp(u, pkeys, cname2, hb, pbkey2.get(), mess))

    namelab2.grid(row=0, column=0, sticky=tk.E)
    cname2.grid(row=0, column=1)
    pblab2.grid(row=1, column=0, sticky=tk.E)
    pbkey2.grid(row=1, column=1)
    sciphr.grid(row=2, column=0, columnspan=2, pady=5)

# Delet Menu
    frd = tk.Frame(fr, bg=b)

    v2 = tk.StringVar()
    v2.set("SELECT")
    drop2 = tk.OptionMenu(frd, v2, *lstl)
    drop2.grid(row=0, column=0, padx=5)

    dc = 'Delete Contact'
    sendciph = tk.Button(frd, bg=w, text=dc, relief=tk.FLAT, command=lambda: del_con(u, v2.get(), hb, mess))
    sendciph.grid(row=0, column=1, sticky=tk.N)

# View Info
    fri = tk.Frame(fr, bg=b)
    pkeys = con.base(con.decrypt(u.pkeys, hb, hb), alf.hexd, alf.hexsplit)
    pkeys = pkeys.split("l")

    pkeylab = tk.Label(fri, text='Public Key: ', bg=b, fg=w)
    pkeylab.grid(row=0, column=0)

    urpkey = tk.Entry(fri, relief=tk.FLAT, bg=b, fg=w)
    urpkey.insert(tk.INSERT, pkeys[0] + "l" + pkeys[1])
    urpkey.grid(row=0, column=1)

    framez = [fr1, fr3, fra, frd, fri, frm]

    menu_swap(framez, fr3)

    root.config(menu=menubar)


def cwrap(youser, tx, contact, en, hb, message):

    # This function is multipurpose, it either encrypts or decrypts based on the second value passed in
    # Retrieve the keys (names) of all the contacts and print them out for the user to select

    themessage = tx.get("1.0", 'end-1c')

    if contact == 'select':
        displ(message, 'No User Selected', 'Red')
        return

    cipher = ''

    for c in youser.contactlist:
        if contact == c['name']:
            cipher = c['cipher']

    if contact == 'self':
        cipher = hb

    if en:

        # Converts the message to hexidecimal since the crypt function only works with
        # A nonce is packaged with the message to avoid reusing the same cipher each time which would make the
        # cipher vulnerable

        themedium = con.base(themessage)
        nonce = uu.uuid4().hex
    else:

        # Apologies for the McLuhan reference

        themedium = con.base(themessage, alfout=alf.hexsplit)

        if themedium.find('l') == -1:
            displ(message, "Not Decryptable", 'Red')
            return
        else:
            nonce = themedium.split("l")[1]
            themedium = themedium.split("l")[0]

    # Finally the message is ready to be encrypted or decrypted using the crypt() function

    encrypted_message = con.crypt(themedium, cipher, nonce, en)

    if en:
        encrypted_message += "l" + nonce
        final_message = con.base(encrypted_message, alf.hexsplit, alf.full)
    else:
        final_message = con.base(encrypted_message, alf.hexd, alf.full)

    tx.delete("1.0", 'end-1c')
    tx.insert(tk.INSERT, final_message)
    tx['fg'] = 'Black'


def menu_swap(frz, frq):

    for f in frz:
        f.grid_forget()

    frq.grid(row=0, column=0)


def menu_drop(frf, fra):

    frf.grid_forget()

    fra.grid_forget()


def mkc(user, pubk, contname, hashbass, message):

    if contname == 'select' or contname == 'Self':
        displ(message, 'Nice Try', 'Red')
        return

    if pubk.find('l') == -1:
        displ(message, 'Invalid Public Key', 'Red')
        return

    pubk = pubk.split("l")
    fmodulus = int(pubk[0])

    cipher = uu.uuid4().hex
    int_ciph = con.toint(cipher, alf.hexd)

    miniciph = int_ciph % fmodulus
    finalciph = con.tostring(miniciph, alf.hexd)

    enc_ciph = con.pcrypt(fmodulus, int(pubk[1]), miniciph)

    displ(message, "Encrypted Cipher: " + str(enc_ciph))
    ret.importciph(user, contname, finalciph, hashbass)


def imp(user, pkeys, cname, hashbass, ciph, message):

    contname = cname.get()

    if not ciph.isdecimal():
        message.delete(0, tk.END)
        message.insert(tk.INSERT, 'Not A Valid Cipher')
        return

    modulus = int(pkeys[0])
    privkey = int(pkeys[2])
    ciph = int(ciph)
    if ret.oldcontact(contname, user):
        message.insert(tk.INSERT, 'Contact already exists')
        return

    ciph = con.tostring(con.pcrypt(modulus, privkey, ciph), alf.hexd)

    ret.importciph(user, contname, ciph, hashbass)

    displ(message, 'Contact Added')


def del_con(user, contd, hashbass, message):

    for c in user.contactlist:
        if c['name'] == contd:
            user.contactlist.remove(c)
            ret.savecontacts(user, hashbass)
            displ(message, 'Contact Deleted')
            return
    displ(message, 'Contact not found')


def logout(frz, frq):

    namebox.delete(0, tk.END)
    passbox.delete(0, tk.END)

    menu_swap(frz, frq)

    emptymenu = tk.Menu(root)
    root.config(menu=emptymenu)


def displ(message, txt, col='White'):
    message.delete(0, tk.END)
    message.insert(tk.INSERT, txt)
    message['fg'] = col


ret.populate_user_list()

root = tk.Tk()
root.wm_title('Shroud')
fr = tk.Frame(root, bg="black", bd=10)
fr1 = tk.Frame(fr, bg="black", bd=0)

nametag = tk.Label(fr1, text="Username", bg="Black", fg="WHITE", anchor=tk.E)
nametag.grid(row=0, column=0, sticky=tk.E)

namebox = tk.Entry(fr1, relief=tk.FLAT, width=22)
namebox.grid(row=0, column=1, columnspan=2, sticky=tk.W, padx=1, pady=1)

passtag = tk.Label(fr1, text="Password", bg="Black", fg="WHITE")
passtag.grid(row=1, column=0, sticky=tk.E)

passbox = tk.Entry(fr1, relief=tk.FLAT, show="*", width=22)
passbox.grid(row=1, column=1, columnspan=2, sticky=tk.W, padx=1, pady=1)

error_label = tk.Label(fr1, text="", bg="Black", fg="RED")
error_label.grid(row=3, columnspan=3)

ca = tk.Button(fr1, text="Create Account", relief=tk.FLAT, bg="WHITE", bd=0, command=signup)
ca.grid(row=2, column=1, padx=1, pady=1, sticky=tk.W)

si = tk.Button(fr1, text="Sign In", relief=tk.FLAT, bg="WHITE", bd=0, command=signin)
si.grid(row=2, column=2, padx=1, pady=1, sticky=tk.E)

fr.pack()
fr1.grid(row=0, column=0)
root.mainloop()
