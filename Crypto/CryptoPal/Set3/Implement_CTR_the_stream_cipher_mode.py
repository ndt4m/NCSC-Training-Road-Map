"""Implement CTR, the stream cipher mode
The string:

L77na/nrFsKvynd6HzOoG7GHTLXsTVu9qvY/2syLXzhPweyyMTJULu/6/kXX0KSvoOLSFQ==
... decrypts to something approximating English in CTR mode, which is an AES block cipher mode that turns AES into a stream cipher, with the following parameters:

      key=YELLOW SUBMARINE
      nonce=0
      format=64 bit unsigned little endian nonce,
             64 bit little endian block count (byte count / 16)
CTR mode is very simple.

Instead of encrypting the plaintext, CTR mode encrypts a running counter, producing a 16 byte block of keystream, which is XOR'd against the plaintext.

For instance, for the first 16 bytes of a message with these parameters:

keystream = AES("YELLOW SUBMARINE",
                "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")
... for the next 16 bytes:

keystream = AES("YELLOW SUBMARINE",
                "\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00")
... and then:

keystream = AES("YELLOW SUBMARINE",
                "\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00")
CTR mode does not require padding; when you run out of plaintext, you just stop XOR'ing keystream and stop generating keystream.

Decryption is identical to encryption. Generate the same keystream, XOR, and recover the plaintext.

Decrypt the string at the top of this function, then use your CTR function to encrypt and decrypt other things.

This is the only block cipher mode that matters in good code.
Most modern cryptography relies on CTR mode to adapt block ciphers into stream ciphers, because most of what we want to encrypt is better described as a stream than as a sequence of blocks. Daniel Bernstein once quipped to Phil Rogaway that good cryptosystems don't need the "decrypt" transforms. Constructions like CTR are what he was talking about.
"""


import base64
import os
import sys
sys.path.append(os.path.realpath("Set1"))
from AES_in_ECB_mode import encryptAES
sys.path.remove(os.path.realpath("Set1"))
from pwn import xor
import math

def encrypt_CTR(plaintext, key, nonce):
    ctx = b""
    keyStreams = [encryptAES(nonce+int(i).to_bytes(8, "little"), key) for i in range(math.ceil(len(plaintext)/16))]
    for i in range(math.ceil((len(plaintext)/16))):
        ctx += xor(plaintext[i*16:i*16+16], keyStreams[i][:len(plaintext[i*16:i*16+16])])
        
    return ctx

def decrypt_CTR(ciphertext, key, nonce):
    plt = b""
    keyStreams = [encryptAES(nonce+int(i).to_bytes(8, "little"), key) for i in range(math.ceil(len(ciphertext)/16))]
    for i in range(math.ceil(len(ciphertext)/16)):
        plt += xor(ciphertext[i*16:i*16+16], keyStreams[i][:len(ciphertext[i*16:i*16+16])])
    return plt

if __name__ == "__main__":
    ctx = base64.b64decode("L77na/nrFsKvynd6HzOoG7GHTLXsTVu9qvY/2syLXzhPweyyMTJULu/6/kXX0KSvoOLSFQ==")
    print(len(ctx))
    key = b"YELLOW SUBMARINE"
    nonce = bytes(8)

    print(decrypt_CTR(ctx, key, nonce))