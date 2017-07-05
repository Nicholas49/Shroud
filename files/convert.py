import math
import hashlib


# These are functions that take in some data and return it in an altered form
# It can generally be devided into 3 categories: functions that encrypt/decrypt, hash, or convert the base of a string


def base(text,
         alfin="0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ ',./=-;<>?+_:!@#$%^&*()[]{}`~|",
         alfout="0123456789abcdef"):
    return tostring(toint(text, alfin), alfout)


def crypt(hext, hexkey, salt, en):
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


def encrypt(hext, hexkey, salt="none"):
    return crypt(hext, hexkey, salt, True)


def decrypt(hext, hexkey, salt="none"):
    return crypt(hext, hexkey, salt, False)


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
