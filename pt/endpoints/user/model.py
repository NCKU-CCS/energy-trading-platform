import uuid
from werkzeug.security import generate_password_hash

from config import db
from utils.base_models import ETBaseMixin


class User(db.Model, ETBaseMixin):
    __tablename__ = 'user'
    uuid = db.Column(db.String(40), primary_key=True, unique=True, nullable=False)
    account = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), unique=False, nullable=False)
    username = db.Column(db.String(80), unique=False, nullable=False)
    tag = db.Column(db.String(120), unique=True, nullable=False)  # Login Bearer Tag
    avatar = db.Column(db.String(120))
    balance = db.Column(db.Integer)
    address = db.Column(db.String(120))
    eth_address = db.Column(db.String(80))

    # fmt: off
    def __init__(self, account, password, username, tag, avatar, balance, address, eth_address):
        self.uuid = str(uuid.uuid4())
        self.account = account
        self.password = generate_password_hash(password)
        self.username = username
        self.tag = tag
        self.avatar = avatar
        self.balance = balance
        self.address = address
        self.eth_address = eth_address
    # fmt: on
