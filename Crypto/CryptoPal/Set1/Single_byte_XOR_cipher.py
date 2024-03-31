"""Single-byte XOR cipher
The hex encoded string:

1b37373331363f78151b7f2b783431333d78397828372d363c78373e783a393b3736
... has been XOR'd against a single character. Find the key, decrypt the message.

You can do this by hand. But don't: write code to do it for you.

How? Devise some method for "scoring" a piece of English plaintext. Character frequency is a good metric. Evaluate each output and choose the one with the best score.

Achievement Unlocked
You now have our permission to make "ETAOIN SHRDLU" jokes on Twitter.
"""
from pwn import xor
def score(plaintext):
    scale = {
        0: list("e"),
        1: list("taoinshr"),
        2: list("dl"),
        3: list("cumwfgypb"),
        4: list("vkjxqz")
        
    }
    for key in scale.keys():
        for char in scale[key]:
            if ord(char) not in plaintext:
                scale[key].remove(char)
    group0_count, group1_count, group2_count, group3_count, group4_count = len(scale[0]), len(scale[1]), len(scale[2]), len(scale[3]), len(scale[4])
    score = 0
    for i in range(len(plaintext)):
        if plaintext[i] in list(range(0, 65)) + list(range(91, 97)) + list(range(123, 128)):
            score -= 1
        elif i == 0 and chr(plaintext[0]) in scale[0]:
            score += 1
        elif i in range(group0_count, group1_count+1) and chr(plaintext[i]) in scale[1]:
            score += 1
        elif i in range(group1_count+1, group2_count+1) and chr(plaintext[i]) in scale[2]:
            score += 1
        elif i in range(group2_count+1, group3_count+1) and chr(plaintext[i]) in scale[3]:
            score += 1
        elif i in range(group3_count+1, group4_count+1) and chr(plaintext[i]) in scale[4]:
            score += 1
    return score 
        
            
def char_frequency(plaintext):
    Dict = {}
    for char in plaintext.lower():
        if char == 32:
            continue
        if char in Dict:
            Dict[char] += 1
        else:
            Dict[char] = 1
    sorted_keys = list({k: v for k, v in sorted(Dict.items(), key=lambda item: item[1], reverse=True)}.keys())
    return sorted_keys

def findPlaintext(hex_string):
    s = bytes.fromhex(hex_string)
    res = {}
    for key in range(1, 128):
        xored = xor(s, key.to_bytes(1, 'big'))
        res[(xored, chr(key))] = score(char_frequency(xored))
    max_v = max(res.values())
    max_k = []
    for k, v in res.items():
        if v == max_v:
            max_k.append(k)
    return (max_k, max_v)
    
if __name__=="__main__":

    print(findPlaintext("1b37373331363f78151b7f2b783431333d78397828372d363c78373e783a393b3736"))
       