import math
import random


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
