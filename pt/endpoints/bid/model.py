import uuid
from datetime import datetime

from config import db

# pylint: disable=W0611
from utils.base_models import ETBaseMixin
from ..user.model import User # NOQA

# pylint: enable=W0611


class Tenders(db.Model, ETBaseMixin):
    __tablename__ = 'tenders'
    uuid = db.Column(db.String(40), primary_key=True, unique=True, nullable=False)
    bid_type = db.Column(db.String(40))  # sell or buy
    start_time = db.Column(db.DateTime, unique=False, nullable=False)
    end_time = db.Column(db.DateTime, unique=False, nullable=False)
    # ForeignKey to Tenders
    user_id = db.Column(db.String(80), db.ForeignKey('user.uuid'), nullable=False)
    user = db.relationship('User')


class MatchResult(db.Model, ETBaseMixin):
    __tablename__ = 'matchresult'
    uuid = db.Column(db.String(40), primary_key=True, unique=True, nullable=False)
    bid_type = db.Column(db.String(40))  # sell or buy
    start_time = db.Column(db.DateTime, unique=False, nullable=False)
    end_time = db.Column(db.DateTime, unique=False, nullable=False)
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
    # ForeignKey to Tenders
    tenders_id = db.Column(db.String(80), db.ForeignKey('tenders.uuid'), nullable=False)
    tenders = db.relationship('Tenders')

    # pylint: disable=R0914,C0301
    def __init__(self, bid_type, start_time, end_time, win, status, counterpart_name, counterpart_address, bid_value, bid_price, win_value, win_price, achievement, settlement, transaction_hash, upload, user_id): # NOQA
        self.uuid = str(uuid.uuid4())
        self.type = bid_type
        self.start_time = start_time
        self.end_time = end_time
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


class BidSubmit(db.Model, ETBaseMixin):
    __tablename__ = 'bidsubmit'
    uuid = db.Column(db.String(40), primary_key=True, unique=True, nullable=False)
    bid_type = db.Column(db.String(40))  # sell or buy
    start_time = db.Column(db.DateTime, unique=False, nullable=False)
    end_time = db.Column(db.DateTime, unique=False, nullable=False)
    value = db.Column(db.Float)
    price = db.Column(db.Float)
    upload_time = db.Column(db.Date, unique=False, nullable=False)
    # ForeignKey to Bid
    tenders_id = db.Column(db.String(80), db.ForeignKey('tenders.uuid'), nullable=False)
    tenders = db.relationship('Tenders')

    def __init__(self, bid_type, start_time, end_time, value, price, bid_id):
        self.uuid = str(uuid.uuid4())
        self.bid_type = bid_type
        self.start_time = start_time
        self.end_time = end_time
        self.value = value
        self.price = price
        self.upload_time = datetime.today()
        self.bid_id = bid_id
