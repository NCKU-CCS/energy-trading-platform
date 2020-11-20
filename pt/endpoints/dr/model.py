from datetime import datetime, timedelta

from loguru import logger

from config import db
from utils.base_models import UTCDatetime

# pylint: disable=W0611
from utils.base_models import ETBaseMixin
from ..user.model import User  # NOQA

# pylint: enable=W0611


class DRBidModel(db.Model, ETBaseMixin):
    __tablename__ = "DR_bid"
    executor = db.Column(db.String(), nullable=False)
    acceptor = db.Column(db.String(), nullable=True)
    start_time = db.Column(UTCDatetime, nullable=False)
    end_time = db.Column(UTCDatetime, nullable=True)
    volume = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)
    result = db.Column(db.Boolean, nullable=True)
    status = db.Column(db.String(), nullable=True)
    rate = db.Column(db.Float, nullable=True)
    settlement = db.Column(db.Float, nullable=True)
    blockchain_url = db.Column(db.String(), nullable=True)


def user_add_bid(bid: dict):
    bid["status"] = "已投標"
    # set start time to bid day (tomorrow)
    bid["start_time"] = get_tomorrow()
    logger.debug(f"[user add bid] add {bid}")
    try:
        DRBidModel(**bid).add()
    except Exception as error:
        logger.error(f"[user add bid] error: {error}")
        DRBidModel.rollback()
        return False
    return True


def aggregator_accept(acceptor: str, uuids: list, start: datetime, end: datetime):
    tomorrow = get_tomorrow()
    day_after_tomorrow = get_tomorrow(tomorrow)
    # check time available
    if not (tomorrow <= start <= day_after_tomorrow) and (tomorrow <= end <= day_after_tomorrow):
        logger.error(f"[aggregator accept] start, end time invalid")
        logger.debug(f"[aggregator accept] start time: {tomorrow <= start <= day_after_tomorrow}")
        logger.debug(f"[aggregator accept] end time: {tomorrow <= end <= day_after_tomorrow}")
        return None, None
    success = list()
    failure = list()
    # GET ALL BIDS, if not accept -> reject
    criteria = (DRBidModel.start_time >= tomorrow, DRBidModel.end_time < day_after_tomorrow)
    bids = DRBidModel.query.filter(*criteria).all()
    for bid in bids:
        try:
            if bid.uuid in uuids:
                logger.debug(f"[aggregator accept] Accept {bid.uuid}")
                # Accept bids
                bid.acceptor = acceptor
                bid.start_time = start
                bid.end_time = end
                bid.result = True
                bid.status = "已得標"
                DRBidModel.update(bid)
                success.append(bid.uuid)
            else:
                logger.debug(f"[aggregator accept] Reject {bid.uuid}")
                # Reject bids
                bid.acceptor = None
                bid.start_time = tomorrow
                bid.end_time = None
                bid.result = False
                bid.status = "未得標"
                DRBidModel.update(bid)
        except Exception as error:
            logger.error(f"[aggregator accept] error: {error}")
            failure.append(bid.uuid)
            DRBidModel.rollback()
    return success, failure


def get_tomorrow(today: datetime = datetime.today()):
    tomorrow = today + timedelta(days=1)
    return get_start_of_day(tomorrow)


def get_start_of_day(day: datetime):
    return datetime.combine(day.date(), datetime.min.time())
