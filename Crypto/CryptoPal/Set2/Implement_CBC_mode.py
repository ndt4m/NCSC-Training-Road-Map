"""Implement CBC mode
CBC mode is a block cipher mode that allows us to encrypt irregularly-sized messages, despite the fact that a block cipher natively only transforms individual blocks.

In CBC mode, each ciphertext block is added to the next plaintext block before the next call to the cipher core.

The first plaintext block, which has no associated previous ciphertext block, is added to a "fake 0th ciphertext block" called the initialization vector, or IV.

Implement CBC mode by hand by taking the ECB function you wrote earlier, making it encrypt instead of decrypt (verify this by decrypting whatever you encrypt to test), and using your XOR function from the previous exercise to combine them.

The file here is intelligible (somewhat) when CBC decrypted against "YELLOW SUBMARINE" with an IV of all ASCII 0 (\x00\x00\x00 &c)

Don't cheat.
Do not use OpenSSL's CBC code to do CBC mode, even to verify your results. What's the point of even doing this stuff if you aren't going to learn from it?
"""
import os
import sys
sys.path.append(os.path.realpath("Set1"))
from AES_in_ECB_mode import decryptAES, encryptAES
sys.path.remove(os.path.realpath("Set1"))
import base64
from Implement_PKCS7_padding import pkcs7
from pwn import xor

iv = b"\x00"*16
key = b"YELLOW SUBMARINE"

ctx = ""
with open("Set2\Implement_CBC_mode.txt", "r") as f:
    ctx = base64.b64decode(f.read().replace("\n", ""))

def decrypt_CBC(ciphertext, key, iv):
    """Decrypt the ciphertext using AES decryption in CBC mode.

    Args:
        ciphertext (byte string): The ciphertext need to decrypt
        key (byte string): The key use to decrypt the ciphertext
        iv (byte string): The initilization vector (IV) use to decrypt

    Returns:
        byte string: The plaintext decrypted
    """    
    plaintext = b""
    for i in range(len(ciphertext) // 16):
        plaintext += xor(decryptAES(ciphertext[i*16:i*16+16], key), iv)
        iv = ciphertext[i*16:i*16+16]
    return plaintext


def encrypt_CBC(plaintext, key):
    """Encrypt the plaintext using AES encryption in CBC mode.

    Args:
        plaintext (byte string): The message need to encrypt
        key (byte string): The key use to encrypt

    Returns:
        byte string: The ciphertext encrypted
    """    
    iv = os.urandom(16)
    plaintext = pkcs7(plaintext, 16)
    ciphertext = iv
    for i in range(len(plaintext) // 16):
        ciphertext += encryptAES(xor(plaintext[i*16:i*16+16], ciphertext[i*16:i*16+16]), key)
    
    return ciphertext

if __name__ == "__main__":
    
    plt = b"i'm the one who destroys this challenge"
    key = b"you won't know"
    ctx = encrypt_CBC(plt, key)    
    iv = ctx[0:16]
    print("ctx:", ctx+b"1234567891234567")
    print("iv:", iv)
    plt = decrypt_CBC(b"1234567891234567"+ctx+b"1234567891234567", key, iv)
    print(plt)
   

