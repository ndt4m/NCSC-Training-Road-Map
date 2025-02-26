"""Byte-at-a-time ECB decryption (Simple)
Copy your oracle function to a new function that encrypts buffers under ECB mode using a consistent but unknown key (for instance, assign a single random key, once, to a global variable).

Now take that same function and have it append to the plaintext, BEFORE ENCRYPTING, the following string:

Um9sbGluJyBpbiBteSA1LjAKV2l0aCBteSByYWctdG9wIGRvd24gc28gbXkg
aGFpciBjYW4gYmxvdwpUaGUgZ2lybGllcyBvbiBzdGFuZGJ5IHdhdmluZyBq
dXN0IHRvIHNheSBoaQpEaWQgeW91IHN0b3A/IE5vLCBJIGp1c3QgZHJvdmUg
YnkK
Spoiler alert.
Do not decode this string now. Don't do it.

Base64 decode the string before appending it. Do not base64 decode the string by hand; make your code do it. The point is that you don't know its contents.

What you have now is a function that produces:

AES-128-ECB(your-string || unknown-string, random-key)
It turns out: you can decrypt "unknown-string" with repeated calls to the oracle function!

Here's roughly how:

Feed identical bytes of your-string to the function 1 at a time --- start with 1 byte ("A"), then "AA", then "AAA" and so on. Discover the block size of the cipher. You know it, but do this step anyway.
Detect that the function is using ECB. You already know, but do this step anyways.
Knowing the block size, craft an input block that is exactly 1 byte short (for instance, if the block size is 8 bytes, make "AAAAAAA"). Think about what the oracle function is going to put in that last byte position.
Make a dictionary of every possible last byte by feeding different strings to the oracle; for instance, "AAAAAAAA", "AAAAAAAB", "AAAAAAAC", remembering the first block of each invocation.
Match the output of the one-byte-short input to one of the entries in your dictionary. You've now discovered the first byte of unknown-string.
Repeat for the next byte.
Congratulations.
This is the first challenge we've given you whose solution will break real crypto. Lots of people know that when you encrypt something in ECB mode, you can see penguins through it. Not so many of them can decrypt the contents of those ciphertexts, and now you can. If our experience is any guideline, this attack will get you code execution in security tests about once a year.
"""

import os
from Implement_PKCS7_padding import pkcs7
import base64
import sys
sys.path.append(os.path.realpath("Set1"))
from AES_in_ECB_mode import encrypt_ECB
sys.path.remove(os.path.realpath("Set1"))

key = os.urandom(16)
def encryption_oracle(input):

    unknown = base64.b64decode("Um9sbGluJyBpbiBteSA1LjAKV2l0aCBteSByYWctdG9wIGRvd24gc28gbXkgaGFpciBjYW4gYmxvdwpUaGUgZ2lybGllcyBvbiBzdGFuZGJ5IHdhdmluZyBqdXN0IHRvIHNheSBoaQpEaWQgeW91IHN0b3A/IE5vLCBJIGp1c3QgZHJvdmUgYnkK")

    plaintext = pkcs7(input+unknown, 16)
    
    return encrypt_ECB(plaintext, key)

def find_flag_len():
    test_input = b"a"
    ctx_len  = len(encryption_oracle(test_input))
    old = ctx_len
    while ctx_len == old:
        test_input = test_input + b"a"
        ctx_len = len(encryption_oracle(test_input))
    return old - len(test_input)

def isECB_encryption():
    test_input = b"a"*64
    ctx = encryption_oracle(test_input)
    if ctx[:16] == ctx[16:32]:
        return True
    return False


def break_the_encryption_oracle():
    flag_len = find_flag_len()
    if not isECB_encryption():
        return "<---Cannot break this machine--->"
    
    num_blocks_to_hold_flag = flag_len // 16 + 1
    # convert to bytes
    size = num_blocks_to_hold_flag * 16
    flag = b""
    while len(flag) < flag_len:
        
        missing_byte_block =b"a"*(size - 1 - len(flag))
        full_byte_block = encryption_oracle(missing_byte_block)[:size]

        possible_bytes = [b"e", b"E", b"a", b"A", b"u", b"U", b"i", b"I", b"o", b"O", b"p", b"P", b"q", b"Q", b"w", b"W", b"r", b"R", b"t", b"T", b"y", b"Y", b"Z", b"z", b"x", b"X", b"s", b"S", b"d", b"D", b"f", b"F", b"g", b"G", b"H", b"h", b"J", b"j", b"k", b"K", b"l", b"L", b"c", b"C", b"v", b"V", b"b", b"B", b"n", b"N", b"M", b"m"] + [bytes([i]) for i in range(65)] + [bytes([i]) for i in range(91, 97)] + [bytes([i]) for i in range(123, 128)]
        for missing_byte in possible_bytes:
            if encryption_oracle(missing_byte_block+flag+missing_byte)[:size] == full_byte_block:
                flag += missing_byte
                break
    return flag
print(break_the_encryption_oracle())
    