"""ECB cut-and-paste
Write a k=v parsing routine, as if for a structured cookie. The routine should take:

foo=bar&baz=qux&zap=zazzle
... and produce:

{
  foo: 'bar',
  baz: 'qux',
  zap: 'zazzle'
}
(you know, the object; I don't care if you convert it to JSON).

Now write a function that encodes a user profile in that format, given an email address. You should have something like:

profile_for("foo@bar.com")
... and it should produce:

{
  email: 'foo@bar.com',
  uid: 10,
  role: 'user'
}
... encoded as:

email=foo@bar.com&uid=10&role=user
Your "profile_for" function should not allow encoding metacharacters (& and =). Eat them, quote them, whatever you want to do, but don't let people set their email address to "foo@bar.com&role=admin".

Now, two more easy functions. Generate a random AES key, then:

    A. Encrypt the encoded user profile under the key; "provide" that to the "attacker".
    B. Decrypt the encoded user profile and parse it.
Using only the user input to profile_for() (as an oracle to generate "valid" ciphertexts) and the ciphertexts themselves, make a role=admin profile.
"""
import os
import random
from pwn import xor
import sys
sys.path.append(os.path.realpath("Set1"))
from AES_in_ECB_mode import encrypt_ECB, decrypt_ECB
from Implement_CBC_mode import encrypt_CBC, decrypt_CBC
sys.path.remove(os.path.realpath("Set1"))
from Implement_PKCS7_padding import pkcs7

key = os.urandom(16)
def parsing_routine(text):
  res = {}
  for element in text.split("&"):
    splited = element.split("=")
    if len(splited) == 2:
      k, v = element.split("=")
      res[k.strip()] = v.strip()
  return res

#<------------------------------------------------ECB VERSION------------------------------------------------>

def profile_for_1(email): # ECB version
  encoded = "email={email}&uid={uid}&role=user".format(email=email.replace("&", "").replace("=", ""), uid=random.randrange(1,101)).encode("ascii")
  return encrypt_ECB(pkcs7(encoded, 16), key)


ctx = profile_for_1("a"*10 + pkcs7(b"admin", 16).decode("ascii") +"a"*3)
admin_encryption = ctx[16:32]
# role_encryption = ctx[32:48]
new_ctx = ctx[:48]  + admin_encryption
res = parsing_routine(decrypt_ECB(new_ctx, key).decode("ascii"))
while len(res["uid"]) != 2:
  ctx = profile_for_1("a"*10 + pkcs7(b"admin", 16).decode("ascii") +"a"*3)
  admin_encryption = ctx[16:32]
  new_ctx = ctx[:48] + admin_encryption
  res = parsing_routine(decrypt_ECB(new_ctx, key).decode("ascii"))
print(res)

#<------------------------------------------------CBC VERSION------------------------------------------------>
def profile_for_2(email): # CBC VERSION
  encoded = "email={email}&uid={uid}&role=user".format(email=email.replace("&", "").replace("=", ""), uid=random.randrange(1,101)).encode("ascii")
  return encrypt_CBC(encoded, key)

ctx = profile_for_2("a"*19)
iv = ctx[:16]
ctx = ctx[16:]
byte_role_admin = xor(xor(pkcs7(b"&role=admin", 16), ctx[16:32]), pkcs7(b"&role=user", 16))
new_ctx = ctx[:32] + byte_role_admin + ctx[32:]
plt = ""
for byte in decrypt_CBC(new_ctx, key, iv):
  plt += chr(byte)
res = parsing_routine(plt)
while "role" not in res.keys():
  ctx = profile_for_2("a"*19)
  iv = ctx[:16]
  ctx = ctx[16:]
  byte_role_admin = xor(xor(pkcs7(b"&role=admin", 16), ctx[16:32]), pkcs7(b"&role=user", 16))
  new_ctx = ctx[:32] + byte_role_admin + ctx[32:]
  plt = ""
  for byte in decrypt_CBC(new_ctx, key, iv):
    plt += chr(byte)
  res = parsing_routine(plt)
print(res)

