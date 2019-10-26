import os
import iota
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from Cryptodome import Random
from Cryptodome.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Cryptodome.Signature import PKCS1_v1_5 as Signature_pkcs1_v1_5
from Cryptodome.PublicKey import RSA


load_dotenv()

# pylint: disable=C0103
app = Flask(__name__)
SQLALCHEMY_DATABASE_URI = os.environ.get('DB_URL', 'postgresql://dev_user:dev191026@localhost:5432/dev_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
# pylint: enable=C0103

SEED = os.environ.get('SEED', 'OLYBZRTBYZCJXCJR9WTSHTVXJ9DTWSREFAXIAFPPEAXJAWINDFAOPCSTGVHSJQ9DJRYOUPAEZVLZKWHTZ')
API = iota.Iota(
    os.environ.get('API_URI_TRACKER', 'https://nodes.thetangle.org:443'),
    SEED,
)
API_TRACK = iota.Iota(os.environ.get('API_URI_TRACKER', 'https://nodes.thetangle.org:443'))
TAG_TEMPLATE = [
    'BEMS9HOMEPAGE9INFORMATION9',
    'BEMS9ESS9DISPLAY9',
    'BEMS9EV9DISPLAY9',
    'BEMS9PV9DISPLAY9',
    'BEMS9WT9DISPLAY9'
]

# random
RANDOM_GENERATOR = Random.new().read

PEM_PATH = os.environ.get('PEM_PATH', '/home/energy-trading-platform/pt/rsa')
# decrypt
PLAT_RSA_PRI_KEY = RSA.importKey(open(os.path.join(PEM_PATH, 'plat_rsa_private.pem')).read())
PLAT_CIPHER = Cipher_pkcs1_v1_5.new(PLAT_RSA_PRI_KEY)

# signature
AMI_RSA_PUB_KEY = RSA.importKey(open(os.path.join(PEM_PATH, 'ami_rsa_public.pem')).read())
PLAT_SIGNER = Signature_pkcs1_v1_5.new(AMI_RSA_PUB_KEY)
