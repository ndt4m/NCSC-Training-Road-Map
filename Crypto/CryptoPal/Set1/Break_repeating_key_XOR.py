"""Break repeating-key XOR
It is officially on, now.
This challenge isn't conceptually hard, but it involves actual error-prone coding. The other challenges in this set are there to bring you up to speed. This one is there to qualify you. If you can do this one, you're probably just fine up to Set 6.

There's a file here. It's been base64'd after being encrypted with repeating-key XOR.

Decrypt it.

Here's how:

Let KEYSIZE be the guessed length of the key; try values from 2 to (say) 40.
Write a function to compute the edit distance/Hamming distance between two strings. The Hamming distance is just the number of differing bits. The distance between:
this is a test
and
wokka wokka!!!
is 37. Make sure your code agrees before you proceed.
For each KEYSIZE, take the first KEYSIZE worth of bytes, and the second KEYSIZE worth of bytes, and find the edit distance between them. Normalize this result by dividing by KEYSIZE.
The KEYSIZE with the smallest normalized edit distance is probably the key. You could proceed perhaps with the smallest 2-3 KEYSIZE values. Or take 4 KEYSIZE blocks instead of 2 and average the distances.
Now that you probably know the KEYSIZE: break the ciphertext into blocks of KEYSIZE length.
Now transpose the blocks: make a block that is the first byte of every block, and a block that is the second byte of every block, and so on.
Solve each block as if it was single-character XOR. You already have code to do this.
For each block, the single-byte XOR key that produces the best looking histogram is the repeating-key XOR key byte for that block. Put them together and you have the key.
This code is going to turn out to be surprisingly useful later on. Breaking repeating-key XOR ("Vigenere") statistically is obviously an academic exercise, a "Crypto 101" thing. But more people "know how" to break it than can actually break it, and a similar technique breaks something much more important.

No, that's not a mistake.
We get more tech support questions for this challenge than any of the other ones. We promise, there aren't any blatant errors in this text. In particular: the "wokka wokka!!!" edit distance really is 37.
"""
from Single_byte_XOR_cipher import findPlaintext, score, char_frequency
import base64
from pwn import xor
    
def editHammingDistance(s1, s2):
    if len(s1) != len(s2):
        raise ValueError("Hamming distance: The length of s1 must be equal to the length of s2")
    cost = 0
    max_len = max(len(bin(int(s1.encode().hex(), 16))), len(bin(int(s2.encode().hex(), 16))))
    for i, j in zip(bin(int(s1.encode().hex(), 16)).zfill(max_len), bin(int(s2.encode().hex(), 16)).zfill(max_len)):
        if i != j:
            cost += 1
    return cost/max_len

text = ""
with open("Set1\Break_repeating_key_XOR.txt", "r") as f:
    text = base64.b64decode(f.read().replace("\n", ""))
    
    
Dict = {}
for keySize in range(2, 40):
    Dict[keySize] = sum([editHammingDistance(text[keySize*i:i*keySize+keySize].decode("utf-8"), text[keySize*(i+1):(i+1)*keySize+keySize].decode("utf-8")) for i in range(0, (len(text)//keySize)-1)])/((len(text)//keySize)-1)
Dict = {k: v for k, v in sorted(Dict.items(), key=lambda item: item[1])}
key_size = list(Dict.keys())[0]

blocks = [text[key_size*i:i*key_size+key_size] for i in range(len(text)//key_size+1)]
tranposed_bocks = []
for i in range(key_size):
    tmp = b""
    for block in blocks:
        if i < len(block):
            tmp += chr(block[i]).encode()
    tranposed_bocks.append(tmp.hex())

res = []
for block in tranposed_bocks:
    tmp = findPlaintext(block)
    r = set()
    print("cost = ", tmp[1])
    for i in tmp[0]:
        print(i[1], end=" ")
        r.add(i[1])
    print()
    res.append(r)

keys = [""]
for s in res:
    x = []
    flag = False
    m = keys[::]
    for key in m:
        if len(s) == 1:
            tmp = key
            key += list(s)[0]
            keys.remove(tmp)
            keys.append(key)
        else:
            flag = True
            for c in s: 
                tmp = key
                tmp += c
                x.append(tmp)
            keys.remove(key)
    if flag:
        keys = keys + x

            
print("There are", len(keys), "possible keys")       

table = []
for key in keys:
    plt = xor(text, key.encode())
    table.append((key, score(char_frequency(plt))))

table = sorted(table, key= lambda x: x[1], reverse=True)
print("The final key with highest score is:", table[0][0])   
print("-----------------------------------PLAINTEXT--------------------------------")  
print(xor(text, table[0][0].encode()).decode("utf-8"))

    
    