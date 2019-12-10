import uuid
from datetime import datetime

from config import db

# pylint: disable=W0611
from utils.base_models import ETBaseMixin
from ..user.model import User  # NOQA

# pylint: enable=W0611


class Tenders(db.Model, ETBaseMixin):
    __tablename__ = "tenders"
    uuid = db.Column(db.String(40), primary_key=True, unique=True, nullable=False)
    bid_type = db.Column(db.String(40))  # sell or buy
    start_time = db.Column(db.DateTime, unique=False, nullable=False)
    end_time = db.Column(db.DateTime, unique=False, nullable=False)
    # ForeignKey to Tenders
    user_id = db.Column(db.String(80), db.ForeignKey("user.uuid"), nullable=False)
    user = db.relationship("User")

    def __init__(self, tenders_data):  # NOQA
        self.uuid = str(uuid.uuid4())
        self.bid_type = tenders_data["bid_type"]
        self.start_time = tenders_data["start_time"]
        self.end_time = tenders_data["end_time"]
        self.user_id = tenders_data["user_id"]


class MatchResult(db.Model, ETBaseMixin):
    __tablename__ = "matchresult"
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
    tenders_id = db.Column(db.String(80), db.ForeignKey("tenders.uuid"), nullable=False)
    tenders = db.relationship("Tenders")

    # pylint: disable=R0914,C0301
    def __init__(self, match_data):  # NOQA
        self.uuid = str(uuid.uuid4())
        self.bid_type = match_data["bid_type"]
        self.start_time = match_data["start_time"]
        self.end_time = match_data["end_time"]
        self.win = match_data["win"]
        self.status = match_data["status"]
        self.counterpart_name = match_data["counterpart_name"]
        self.counterpart_address = match_data["counterpart_address"]
        self.bid_value = match_data["bid_value"]
        self.bid_price = match_data["bid_price"]
        self.win_value = match_data["win_value"]
        self.win_price = match_data["win_price"]
        self.achievement = match_data["achievement"]
        self.settlement = match_data["settlement"]
        self.transaction_hash = match_data["transaction_hash"]
        self.upload = match_data["upload"]
        self.tenders_id = match_data["tenders_id"]

    # pylint: enable=R0914,C0301


class BidSubmit(db.Model, ETBaseMixin):
    __tablename__ = "bidsubmit"
    uuid = db.Column(db.String(40), primary_key=True, unique=True, nullable=False)
    bid_type = db.Column(db.String(40))  # sell or buy
    start_time = db.Column(db.DateTime, unique=False, nullable=False)
    end_time = db.Column(db.DateTime, unique=False, nullable=False)
    value = db.Column(db.Float)
    price = db.Column(db.Float)
    upload_time = db.Column(db.DateTime, unique=False, nullable=False)
    # ForeignKey to Bid
    tenders_id = db.Column(db.String(80), db.ForeignKey("tenders.uuid"), nullable=False)
    tenders = db.relationship("Tenders")

    def __init__(self, bid_data):
        self.uuid = str(uuid.uuid4())
        self.bid_type = bid_data["bid_type"]
        self.start_time = bid_data["start_time"]
        self.end_time = bid_data["end_time"]
        self.value = bid_data["value"]
        self.price = bid_data["price"]
        self.upload_time = datetime.today()
        self.tenders_id = bid_data["tenders_id"]


def add_bidsubmit(bid_data, user_id):
    tender_data = {
        "bid_type": bid_data["bid_type"],
        "start_time": bid_data["start_time"],
        "end_time": bid_data["end_time"],
        "user_id": user_id,
    }
    bid_data["tenders_id"] = get_tender_id(tender_data)
    BidSubmit.add(BidSubmit(bid_data))
    return True


def edit_bidsubmit(bid_data, user_id):
    target = BidSubmit.query.filter_by(uuid=bid_data["id"]).first()
    target.bid_type = bid_data["bid_type"]
    target.start_time = bid_data["start_time"]
    target.end_time = bid_data["end_time"]
    target.value = bid_data["value"]
    target.price = bid_data["price"]
    target.upload_time = datetime.today()
    tender_data = {
        "bid_type": bid_data["bid_type"],
        "start_time": bid_data["start_time"],
        "end_time": bid_data["end_time"],
        "user_id": user_id,
    }
    target.tenders_id = get_tender_id(tender_data)
    BidSubmit.update(target)
    return True


def get_tender(tender_data):
    tender = Tenders.query.filter_by(
        bid_type=tender_data["bid_type"],
        start_time=tender_data["start_time"],
        end_time=tender_data["end_time"],
        user_id=tender_data["user_id"],
    ).first()
    return tender


def get_tender_id(tender_data):
    tender = get_tender(tender_data)
    if tender:
        return tender.uuid
    Tenders.add(Tenders(tender_data))
    return get_tender(tender_data).uuid
