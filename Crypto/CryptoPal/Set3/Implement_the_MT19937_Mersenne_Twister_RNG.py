"""Implement the MT19937 Mersenne Twister RNG
You can get the psuedocode for this from Wikipedia.

If you're writing in Python, Ruby, or (gah) PHP, your language is probably already giving you MT19937 as "rand()"; don't use rand(). Write the RNG yourself.
"""


# The coefficients for Mersenne Twister 19937:
w, n, m, r = 32, 624, 397, 31
a = 0x9908B0DF
u, d = 11, 0xFFFFFFFF
s, b = 7, 0x9D2C5680
t, c = 15, 0xEFC60000
l = 18
f = 1812433253

# Create a length n array to store the state of the generator
MT = [0] * n
index = n + 1
lower_mask = (1 << r) - 1 # That is, the binary number of r 1's 
upper_mask = int(bin(~lower_mask)[2:].zfill(w)[-w:], 2)

# Initialize the generator from a seed
def seed_mt(seed):
    global index
    index = n
    MT[0] = seed
    for i in range(1, n):
        MT[i] = int(bin(f * (MT[i-1] ^ (MT[i-1] >> (w - 2))) + i)[2:].zfill(w)[-w:], 2)
        
# Generate the next n values from the series x_i 
def twist():
    global index
    for i in range(0, n):
        x = (MT[i] & upper_mask) | (MT[(i+1) % n] & lower_mask)
        xA = x >> 1
        if x % 2 != 0:
            xA = xA ^ a
        MT[i] = MT[(i + m) % n] ^ xA
    index = 0

# Extract a tempered value based on MT[index]
# Calling twist() every n numbers
def extract_number():
    global index
    if index >= n:
        if index > n:
            raise ValueError("Generator was never seeded")
        twist()
    
    y = MT[index]
    y = y ^ ((y >> u) & d)
    y = y ^ ((y << s) & b)
    y = y ^ ((y << t) & c)
    y = y ^ (y >> l)
    
    index = index + 1
    return int(bin(y)[2:].zfill(w)[-w:], 2)

def random_number_generator(seed = None):
    if seed == None:
        return extract_number()
    seed_mt(seed)
    # return random_number_generator()


            