"""Byte-at-a-time ECB decryption (Harder)
Take your oracle function from #12. Now generate a random count of random bytes and prepend this string to every plaintext. You are now doing:

AES-128-ECB(random-prefix || attacker-controlled || target-bytes, random-key)
Same goal: decrypt the target-bytes.

Stop and think for a second.
What's harder than challenge #12 about doing this? How would you overcome that obstacle? The hint is: you're using all the tools you already have; no crazy math is required.

Think "STIMULUS" and "RESPONSE".
"""

import os
from Implement_PKCS7_padding import pkcs7
import base64
import random
import sys
sys.path.append(os.path.realpath("Set1"))
from AES_in_ECB_mode import encrypt_ECB
sys.path.remove(os.path.realpath("Set1"))


key = os.urandom(16)
rdom_bytes = os.urandom(random.randrange(1, 10001))

def encryption_oracle(input):

    unknown = base64.b64decode("Um9sbGluJyBpbiBteSA1LjAKV2l0aCBteSByYWctdG9wIGRvd24gc28gbXkgaGFpciBjYW4gYmxvdwpUaGUgZ2lybGllcyBvbiBzdGFuZGJ5IHdhdmluZyBqdXN0IHRvIHNheSBoaQpEaWQgeW91IHN0b3A/IE5vLCBJIGp1c3QgZHJvdmUgYnkK")
    plaintext = pkcs7(rdom_bytes+input+unknown, 16)
    
    return encrypt_ECB(plaintext, key)
def isECB_encryption():
    test_input = b"a"*64
    ctx = encryption_oracle(test_input)
    for i in range(len(ctx)//16-1):
        if ctx[i*16] == ctx[i*16+16]:
            return True
    return False

def find_random_bytes_length():
    consecutive_blocks = 6
    remaining_bytes = 0
    first = -99999
    while True:
        count = 0
        last = -99999
        ctx = encryption_oracle(b"a" * ((16 * consecutive_blocks) + 16 - remaining_bytes))
        for i in range(len(ctx)//16):
            if ctx[i*16:i*16+16] == ctx[i*16+16:(i+1)*16+16]:
                if last == -99999:
                    count += 1
                    last = i
                    first = i
                if i == last + 1:
                    count += 1
                    last = i
        if count != consecutive_blocks - 1:
            if remaining_bytes != 0:
                remaining_bytes -= 1
            break 
        else:
            remaining_bytes += 1
    # Length of the random_bytes = 16*k + remaining_bytes
    # To find k, we take the position of first block among (6-1) consecutive blocks - remaining_bytes then dividing by 16 and rounding down 
    k = (first * 16 - remaining_bytes) // 16
    return 16 * k + remaining_bytes

def find_flag_length(random_bytes_len):
    test_input = b"a"
    ctx_len = len(encryption_oracle(test_input))
    old_len = len(encryption_oracle(test_input))
    flag_len = 0
    while True:
        test_input = test_input + b"a"
        ctx_len = len(encryption_oracle(test_input))
        if ctx_len != old_len:
            flag_len = old_len - len(test_input) - random_bytes_len
            break
    return flag_len
    
def break_the_encryption_oracle():
    if not isECB_encryption():
        return "<---Cannot break this machine--->"
    random_bytes_len = find_random_bytes_length()
    flag_len = find_flag_length(random_bytes_len)
    
    number_of_blocks_to_hold_flag = flag_len // 16 + 1
    # convert to bytes
    size = number_of_blocks_to_hold_flag * 16
    
    lacking_bytes_of_random_bytes = (16 - random_bytes_len % 16) if random_bytes_len % 16 != 0 else 0
    bytes_for_completting_random_bytes = lacking_bytes_of_random_bytes * b"a"
    starting_index_of_my_input = random_bytes_len + lacking_bytes_of_random_bytes
    
    flag = b""
    while len(flag) < flag_len:
        missing_byte_block = bytes_for_completting_random_bytes + b"a" * (size - 1 - len(flag))
        full_byte_block = encryption_oracle(missing_byte_block)[starting_index_of_my_input:starting_index_of_my_input+size]

        possible_bytes = [b"e", b"E", b"a", b"A", b"u", b"U", b"i", b"I", b"o", b"O", b"p", b"P", b"q", b"Q", b"w", b"W", b"r", b"R", b"t", b"T", b"y", b"Y", b"Z", b"z", b"x", b"X", b"s", b"S", b"d", b"D", b"f", b"F", b"g", b"G", b"H", b"h", b"J", b"j", b"k", b"K", b"l", b"L", b"c", b"C", b"v", b"V", b"b", b"B", b"n", b"N", b"M", b"m"] + [bytes([i]) for i in range(65)] + [bytes([i]) for i in range(91, 97)] + [bytes([i]) for i in range(123, 128)]
        for missing_byte in possible_bytes:
            if encryption_oracle(missing_byte_block+flag+missing_byte)[starting_index_of_my_input:starting_index_of_my_input+size] == full_byte_block:
                flag += missing_byte
                print(flag)
                break
    return flag
print(break_the_encryption_oracle())