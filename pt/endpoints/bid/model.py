import uuid
from config import db
# pylint: disable=W0611
from ..user.model import User
# pylint: enable=W0611

class Bid(db.Model):
    __tablename__ = 'bid'
    uuid = db.Column(db.String(40), primary_key=True, unique=True, nullable=False)
    bid_type = db.Column(db.String(40))  # sell or buy
    time = db.Column(db.DateTime, unique=False, nullable=False)
    win = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(40))
    counterpart_name = db.Column(db.String(80))
    counterpart_address = db.Column(db.String(120))
    bid_value = db.Column(db.Float)
    bid_price = db.Column(db.Float)
    win_value = db.Column(db.Float)
    win_price = db.Column(db.Float)
    achievement = db.Column(db.Float)
    settlement = db.Column(db.Float)
    transaction_hash = db.Column(db.String(80))
    upload = db.Column(db.DateTime, unique=False, nullable=False)
    # ForeignKey to User
    user_id = db.Column(db.String(80), db.ForeignKey('user.uuid'), nullable=False)
    user = db.relationship('User')

    # pylint: disable=R0914,C0301
    def __init__(self, bid_type, time, win, status, counterpart_name, counterpart_address, bid_value, bid_price, win_value, win_price, achievement, settlement, transaction_hash, upload, user_id):
        self.uuid = str(uuid.uuid4())
        self.type = bid_type
        self.time = time
        self.win = win
        self.status = status
        self.counterpart_name = counterpart_name
        self.counterpart_address = counterpart_address
        self.bid_value = bid_value
        self.bid_price = bid_price
        self.win_value = win_value
        self.win_price = win_price
        self.achievement = achievement
        self.settlement = settlement
        self.transaction_hash = transaction_hash
        self.upload = upload
        self.user_id = user_id
    # pylint: enable=R0914,C0301

    def add(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return self.uuid
