import uuid
from werkzeug.security import generate_password_hash
from config import db


class User(db.Model):
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

    def add(self):
        db.session.add(self)
        db.session.commit()

    # pylint: disable=R0201
    def update(self):
        db.session.commit()
    # pylint: enable=R0201

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return self.uuid
