from datetime import datetime

from sqlalchemy.dialects.postgresql import UUID

from config import db
from utils.base_models import UTCDatetime

# pylint: disable=W0611
from utils.base_models import ETBaseMixin
from ..user.model import User  # NOQA

# pylint: enable=W0611


class Tenders(db.Model, ETBaseMixin):
    __tablename__ = "tenders"
    bid_type = db.Column(db.String(40))  # sell or buy
    start_time = db.Column(UTCDatetime, unique=False, nullable=False)
    end_time = db.Column(UTCDatetime, unique=False, nullable=False)
    # ForeignKey to Tenders
    user_id = db.Column(UUID(), db.ForeignKey("user.uuid"), nullable=False)
    user = db.relationship("User")


class BidSubmit(db.Model, ETBaseMixin):
    __tablename__ = "bidsubmit"
    bid_type = db.Column(db.String(40))  # sell or buy
    start_time = db.Column(UTCDatetime, unique=False, nullable=False)
    end_time = db.Column(UTCDatetime, unique=False, nullable=False)
    win = db.Column(db.Integer)
    status = db.Column(db.String(40))
    counterpart_name = db.Column(db.String(80))
    counterpart_address = db.Column(db.String(120))
    value = db.Column(db.Float)
    price = db.Column(db.Float)
    win_value = db.Column(db.Float)
    win_price = db.Column(db.Float)
    achievement = db.Column(db.Float)
    settlement = db.Column(db.Float)
    transaction_hash = db.Column(db.String(80))
    upload_time = db.Column(UTCDatetime, unique=False, nullable=False)
    # ForeignKey to Tenders
    tenders_id = db.Column(UUID(), db.ForeignKey("tenders.uuid"), nullable=False)
    tenders = db.relationship("Tenders")


def add_bidsubmit(bid_data, user_id):
    tender_data = {
        "bid_type": bid_data["bid_type"],
        "start_time": bid_data["start_time"],
        "end_time": bid_data["end_time"],
        "user_id": user_id,
    }
    bid_data["tenders_id"] = get_tender_id(tender_data)
    bid_data["upload_time"] = datetime.today()
    bid_data["status"] = "投標中"
    BidSubmit(**bid_data).add()
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
    Tenders(**tender_data).add()
    return get_tender(tender_data).uuid
