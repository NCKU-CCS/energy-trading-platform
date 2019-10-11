import uuid
from datetime import datetime
from config import db
from ..bid.model import Bid

class Submit(db.Model):
    __tablename__ = 'submit'
    uuid = db.Column(db.String(40), primary_key=True, unique=True, nullable=False)
    type = db.Column(db.String(40))  # sell or buy
    time = db.Column(db.DateTime, unique=False, nullable=False)
    value = db.Column(db.Float)
    price = db.Column(db.Float)
    upload_time = db.Column(db.Date, unique=False, nullable=False)
    # ForeignKey to Bid
    bid_id = db.Column(db.String(80), db.ForeignKey('bid.uuid'), nullable=False)
    bid = db.relationship(Bid)

    def __init__(self, type, time, value, price, bid_id):
        self.uuid = str(uuid.uuid4())
        self.type = type
        self.time = time
        self.value = value
        self.price = price
        self.upload_time = datetime.today()
        self.bid_id = bid_id

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