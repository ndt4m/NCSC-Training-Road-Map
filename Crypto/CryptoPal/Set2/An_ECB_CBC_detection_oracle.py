"""An ECB/CBC detection oracle
Now that you have ECB and CBC working:

Write a function to generate a random AES key; that's just 16 random bytes.

Write a function that encrypts data under an unknown key --- that is, a function that generates a random key and encrypts under it.

The function should look like:

encryption_oracle(your-input)
=> [MEANINGLESS JIBBER JABBER]
Under the hood, have the function append 5-10 bytes (count chosen randomly) before the plaintext and 5-10 bytes after the plaintext.

Now, have the function choose to encrypt under ECB 1/2 the time, and under CBC the other half (just use random IVs each time for CBC). Use rand(2) to decide which to use.

Detect the block cipher mode the function is using each time. You should end up with a piece of code that, pointed at a block box that might be encrypting ECB or CBC, tells you which one is happening.

"""
import os
import random
from Implement_PKCS7_padding import pkcs7
from Implement_CBC_mode import encrypt_CBC
import sys
sys.path.append(os.path.realpath("Set1"))
from AES_in_ECB_mode import encrypt_ECB
sys.path.remove(os.path.realpath("Set1"))


def encryption_oracle(input):
    
    key = os.urandom(16)
    input = os.urandom(random.randrange(5, 11)) + input + os.urandom(random.randrange(5, 11))
    padded = pkcs7(input, 16)
    
    ctx = b""
    iv = {}
    for i in range(len(padded) // 16):
        mode = random.randrange(0, 2)
        if mode == 0:            
            ctx += encrypt_ECB(padded[i*16:i*16+16], key)
        else:
            res = encrypt_CBC(padded[i*16:i*16+16], key)
            ctx += res[16:]
            iv[res[:16]] = str(i*16)+":"+str(i*16+16)
    return (ctx, iv)

def detect_ecb_cbc(ciphertext):
    for i in range(len(ciphertext)//16):
        if ciphertext[i*16:i*16+16] in ciphertext[i*16+16:]:
            print(str(i*16)+":"+str(i*16+16)+"==> ECB")
        else:
            print(str(i*16)+":"+str(i*16+16)+"==> CBC")
res = encryption_oracle(b"AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
ctx = res[0]
print("ciphertext:", ctx)
print(res[1])
detect_ecb_cbc(ctx)    