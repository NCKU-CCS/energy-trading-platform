from config import db
from utils.base_models import ETBaseMixin


class User(db.Model, ETBaseMixin):
    __tablename__ = "user"
    account = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), unique=False, nullable=False)
    username = db.Column(db.String(80), unique=False, nullable=False)
    tag = db.Column(db.String(120), unique=True, nullable=False)  # Login Bearer Tag
    avatar = db.Column(db.String(120))
    balance = db.Column(db.Integer)
    address = db.Column(db.String(120))
    eth_address = db.Column(db.String(80))
    is_aggregator = db.Column(db.Boolean, unique=False, nullable=True, default=False)
    eth_secret = db.Column(db.String(128))
    contract_creator = db.Column(db.Boolean, unique=False, nullable=False, default=False)
