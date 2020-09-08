import os

import pytz
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from Cryptodome import Random
from Cryptodome.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Cryptodome.Signature import PKCS1_v1_5 as Signature_pkcs1_v1_5
from Cryptodome.PublicKey import RSA


load_dotenv()

# pylint: disable=C0103
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DB_URL", "postgresql://dev_user:dev191026@localhost:5432/dev_db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
# pylint: enable=C0103

SEED = os.environ.get(
    "SEED",
    "OLYBZRTBYZCJXCJR9WTSHTVXJ9DTWSREFAXIAFPPEAXJAWINDFAOPCSTGVHSJQ9DJRYOUPAEZVLZKWHTZ",
)
API_URI = os.environ.get('API_URI', 'https://nodes.thetangle.org:443').split(',')
API_OPEN = os.environ.get('API_OPEN', 'https://nodes.thetangle.org:443')
TAG_TEMPLATE = [
    "BEMS9HOMEPAGE9INFORMATION9",
    "BEMS9ESS9DISPLAY9",
    "BEMS9EV9DISPLAY9",
    "BEMS9PV9DISPLAY9",
    "BEMS9WT9DISPLAY9",
]

# random
RANDOM_GENERATOR = Random.new().read

PEM_PATH = os.environ.get("PEM_PATH", "rsa")
PEM_PATH = os.path.join(os.getcwd(), PEM_PATH)
# decrypt
PLAT_RSA_PRI_KEY = RSA.importKey(
    open(os.path.join(PEM_PATH, "plat_rsa_private.pem")).read()
)
PLAT_CIPHER = Cipher_pkcs1_v1_5.new(PLAT_RSA_PRI_KEY)

# signature
AMI_RSA_PUB_KEY = RSA.importKey(
    open(os.path.join(PEM_PATH, "ami_rsa_public.pem")).read()
)
PLAT_SIGNER = Signature_pkcs1_v1_5.new(AMI_RSA_PUB_KEY)

# the unique secret to form oauth serializer for short-lived token
APP_SECRET_KEY = os.environ.get("APP_SECRET_KEY", "VCn>ZaI],B/K-rPtq|2eB^gps~H>45")

TZ = pytz.timezone(os.environ.get("TZ", "Asia/Taipei"))

# contract related
AES_KEY = os.environ.get("AES_KEY")
INFURA_PROJECT_ID = os.environ.get("INFURA_PROJECT_ID")
CONTRACT_ADDRESS = os.environ.get("CONTRACT_ADDRESS")
ABI_PATH = os.environ.get("ABI_PATH", "pt/contract/")
