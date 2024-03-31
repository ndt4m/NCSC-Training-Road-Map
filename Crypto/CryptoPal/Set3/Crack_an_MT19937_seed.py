"""Crack an MT19937 seed
Make sure your MT19937 accepts an integer seed value. Test it (verify that you're getting the same sequence of outputs given a seed).

Write a routine that performs the following operation:

Wait a random number of seconds between, I don't know, 40 and 1000.
Seeds the RNG with the current Unix timestamp
Waits a random number of seconds again.
Returns the first 32 bit output of the RNG.
You get the idea. Go get coffee while it runs. Or just simulate the passage of time, although you're missing some of the fun of this exercise if you do that.

From the 32 bit RNG output, discover the seed.
"""
import random
import time
from Implement_the_MT19937_Mersenne_Twister_RNG import random_number_generator

def crackMT19937():
    time.sleep(random.randrange(2, 10))
    print("seed =", int(time.time()))
    random_number_generator(int(time.time()))
    time.sleep(random.randrange(2, 10))
    return random_number_generator()



first = crackMT19937()
current = int(time.time())
print("current =", current)
print()
for i in range(current - 1000, current + 1000):
    random_number_generator(i)
    if random_number_generator() == first:
        print("found seed = ", i)
        break

