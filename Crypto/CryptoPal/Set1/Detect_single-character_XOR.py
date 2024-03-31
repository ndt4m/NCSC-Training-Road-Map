"""Detect single-character XOR
One of the 60-character strings in this file has been encrypted by single-character XOR.

Find it.

(Your code from #3 should help.)
"""

from Single_byte_XOR_cipher import findPlaintext 

lines = ""
with open('Set1\Detect_single-character_XOR.txt', 'r') as f:
    lines = f.readlines()

res = {}
for l in lines:
    plt = findPlaintext(l)
    res[plt[1]] = (plt[0], l)

max_k = max(res.keys())
max_v = []
for k, v in res.items():
    if k == max_k:
        max_v.append(v)
print((max_v, max_k))