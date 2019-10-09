import base64
from Cryptodome.Hash import SHA256

from config import PLAT_CIPHER, PLAT_SIGNER, RANDOM_GENERATOR
from utils.utils import get_data

TARGETADDRESS = (
    'WIKETTNX9NVKOGZMOSTXMHFXV9ICADYSVJEPVUPTQQOLEV9YWCSWVPTNF9ETUXEHNJIXZPQWDPDOZ9999'
)


def test():
    message = get_data([TARGETADDRESS])
    # decrypt
    data = PLAT_CIPHER.decrypt(base64.b64decode(message[-1]['data']), RANDOM_GENERATOR)
    print(data)

    # signature
    is_verify = PLAT_SIGNER.verify(
        SHA256.new(data), base64.b64decode(message[-1]['signature'])
    )
    print(is_verify)
