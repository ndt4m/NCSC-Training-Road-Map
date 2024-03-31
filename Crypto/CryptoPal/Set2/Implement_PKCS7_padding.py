"""Implement PKCS#7 padding
A block cipher transforms a fixed-sized block (usually 8 or 16 bytes) of plaintext into ciphertext. But we almost never want to transform a single block; we encrypt irregularly-sized messages.

One way we account for irregularly-sized messages is by padding, creating a plaintext that is an even multiple of the blocksize. The most popular padding scheme is called PKCS#7.

So: pad any block to a specific block length, by appending the number of bytes of padding to the end of the block. For instance,

"YELLOW SUBMARINE"
... padded to 20 bytes would be:

"YELLOW SUBMARINE\x04\x04\x04\x04"

"""


def pkcs7(data_to_pad, block_size):
    if len(data_to_pad) == block_size:
        padding_char = chr(block_size).encode("utf-8")
        return data_to_pad + padding_char*block_size
    elif len(data_to_pad) < block_size:
        padding_char = chr(block_size - len(data_to_pad)).encode("utf-8")
        return data_to_pad + padding_char*(block_size - len(data_to_pad))
    else:
        block_size = ((len(data_to_pad) // block_size) + 1) * block_size
        return pkcs7(data_to_pad, block_size)

if __name__ == "__main__":        
    data_to_pad = b"YELLOW SUBMARINE"
    print(pkcs7(data_to_pad, 20))