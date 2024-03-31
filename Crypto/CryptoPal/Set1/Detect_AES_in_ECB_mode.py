"""Detect AES in ECB mode
In this file are a bunch of hex-encoded ciphertexts.

One of them has been encrypted with ECB.

Detect it.

Remember that the problem with ECB is that it is stateless and deterministic; the same 16 byte plaintext block will always produce the same 16 byte ciphertext.
"""

ctx = ""
with open("Set1\Detect_AES_in_ECB_mode.txt", "r") as f:
    ctx = f.read().split("\n")

for c in ctx:
    for i in range(len(c)//32):
        if c.find(c[i*32:i*32+32], i*32+32) != -1:
            print(c)
            break
