import json, base64
from utils.utils import get_data
from config import plat_cipher, plat_signer, random_generator
from Cryptodome.Hash import SHA256

TARGETADDRESS = 'WIKETTNX9NVKOGZMOSTXMHFXV9ICADYSVJEPVUPTQQOLEV9YWCSWVPTNF9ETUXEHNJIXZPQWDPDOZ9999'

message = get_data([TARGETADDRESS])
# decrypt
data = plat_cipher.decrypt(base64.b64decode(message[-1]['data']), random_generator)
print(data)

# signature
is_verify = plat_signer.verify(SHA256.new(data), base64.b64decode(message[-1]['signature']))
print(is_verify)

# print(data)