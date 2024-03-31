"""Break fixed-nonce CTR statistically
In this file find a similar set of Base64'd plaintext. Do with them exactly what you did with the first, but solve the problem differently.

Instead of making spot guesses at to known plaintext, treat the collection of ciphertexts the same way you would repeating-key XOR.

Obviously, CTR encryption appears different from repeated-key XOR, but with a fixed nonce they are effectively the same thing.

To exploit this: take your collection of ciphertexts and truncate them to a common length (the length of the smallest ciphertext will work).

Solve the resulting concatenation of ciphertexts as if for repeating- key XOR, with a key size of the length of the ciphertext you XOR'd.
"""

import base64
import os
from Implement_CTR_the_stream_cipher_mode import encrypt_CTR
from pwn import xor

text = None
with open("Set3\Break_fixed_nonce_CTR_statistically.txt", "r") as f:
    text = [base64.b64decode(line) for line in f.readlines()]

key = os.urandom(16)
nonce = bytes(8)

ctx = [encrypt_CTR(c, key, nonce) for c in text]

transposed = []
for i in range(max(map(len, ctx))):
    block = []
    for c in ctx:
        if i < len(c):
            block.append(c[i])
    transposed.append(bytes(block))

def rateLetters(byteString):
    letter_count = 0
    for b in byteString:
        if b in list(range(65, 91)) + list(range(97, 123)) + [32]:
            letter_count += 1
    return letter_count / len(byteString)

def findPlaintext(byteString):
    best = None
    for i in range(0, 256):
        plt = xor(byteString, i.to_bytes(1, "little"))
        res = rateLetters(plt)
        if best == None or res > best["letter_rate"]:
            best = {"plaintext": plt, "key": bytes([i]), "letter_rate": res}
    return best

keyStream = b""
for block in transposed:
    keyStream += findPlaintext(block)["key"]

for c in ctx:
    print(xor(c, keyStream[:len(c)]))
