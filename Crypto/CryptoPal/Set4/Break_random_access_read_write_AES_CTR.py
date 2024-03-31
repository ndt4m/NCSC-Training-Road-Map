"""Break "random access read/write" AES CTR
Back to CTR. Encrypt the recovered plaintext from this file (the ECB exercise) under CTR with a random key (for this exercise the key should be unknown to you, but hold on to it).

Now, write the code that allows you to "seek" into the ciphertext, decrypt, and re-encrypt with different plaintext. Expose this as a function, like, "edit(ciphertext, key, offset, newtext)".

Imagine the "edit" function was exposed to attackers by means of an API call that didn't reveal the key or the original plaintext; the attacker has the ciphertext and controls the offset and "new text".

Recover the original plaintext.

Food for thought.
A folkloric supposed benefit of CTR mode is the ability to easily "seek forward" into the ciphertext; to access byte N of the ciphertext, all you need to be able to do is generate byte N of the keystream. Imagine if you'd relied on that advice to, say, encrypt a disk.
"""

import os
import sys
sys.path.append(os.path.realpath("Set3"))
from Implement_CTR_the_stream_cipher_mode import encrypt_CTR, decrypt_CTR
sys.path.remove(os.path.realpath("Set3"))
from base64 import b64decode

ctx = None
with open("Set4\challenge25.txt", "r") as f:
    ctx = b64decode(f.readline())
    
print(ctx)
    
    