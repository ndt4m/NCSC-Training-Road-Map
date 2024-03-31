"""CBC bitflipping attacks
Generate a random AES key.

Combine your padding code and CBC code to write two functions.

The first function should take an arbitrary input string, prepend the string:

"comment1=cooking%20MCs;userdata="
.. and append the string:

";comment2=%20like%20a%20pound%20of%20bacon"
The function should quote out the ";" and "=" characters.

The function should then pad out the input to the 16-byte AES block length and encrypt it under the random AES key.

The second function should decrypt the string and look for the characters ";admin=true;" (or, equivalently, decrypt, split the string on ";", convert each resulting string into 2-tuples, and look for the "admin" tuple).

Return true or false based on whether the string exists.

If you've written the first function properly, it should not be possible to provide user input to it that will generate the string the second function is looking for. We'll have to break the crypto to do that.

Instead, modify the ciphertext (without knowledge of the AES key) to accomplish this.

You're relying on the fact that in CBC mode, a 1-bit error in a ciphertext block:

Completely scrambles the block the error occurs in
Produces the identical 1-bit error(/edit) in the next ciphertext block.
Stop and think for a second.
Before you implement this attack, answer this question: why does CBC mode have this property?


"""
import os
from Implement_PKCS7_padding import pkcs7
from Implement_CBC_mode import encrypt_CBC, decrypt_CBC
from PKCS_7_padding_validation import unpadding
from pwn import xor

key = os.urandom(16)

def parsing_routine(input):
    encoded = ("comment1=cooking%20MCs;userdata="+input.replace(";", "").replace("=", "")+";comment2=%20like%20a%20pound%20of%20bacon").encode("ascii")
    return encrypt_CBC(encoded, key)

def decrypt(ciphertext):
    iv, ctx = ciphertext[:16], ciphertext[16:]
    print(unpadding(decrypt_CBC(ctx, key, iv)))
    if b";admin=true;" in unpadding(decrypt_CBC(ctx, key, iv)):
        return True
    return False
    
ctx = parsing_routine("a"*16)
adding = xor(b"a"*16, b";admin=true;", ctx[32:48])
new_ctx = ctx[:48] + adding + ctx[48:]
print(decrypt(new_ctx))

