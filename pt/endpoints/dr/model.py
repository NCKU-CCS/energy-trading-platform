from datetime import datetime, timedelta, time
from loguru import logger
from random import randint

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
    real_volume = db.Column(db.Float, nullable=True)
    price = db.Column(db.Float, nullable=False)
    result = db.Column(db.Boolean, nullable=True)
    status = db.Column(db.String(), nullable=True)
    rate = db.Column(db.Float, nullable=True)
    settlement = db.Column(db.Float, nullable=True)
    blockchain_url = db.Column(db.String(), nullable=True)
    trading_mode = db.Column(db.Integer, nullable=False)
    order_method = db.Column(db.String(), nullable=False)


def user_add_bid(bid: dict):
    base_time = time(10, 30)
    time_now = datetime.now().time()
    # set bid time
    # before 10:30 | after 10:30
    # bid tomorrow | bid day after tomorrow
    tomorrow = get_tomorrow(datetime.today())
    day_after_tomorrow = get_tomorrow(tomorrow)
    if time_now < base_time:
        bid["start_time"] = tomorrow
    else:
        bid["start_time"] = day_after_tomorrow
    logger.debug(f"[user add bid] add {bid}")
    bid["status"] = "已投標"
    try:
        DRBidModel(**bid).add()
    except Exception as error:
        logger.error(f"[user add bid] error: {error}")
        DRBidModel.rollback()
        return False
    return True


def aggregator_accept(acceptor: str, uuids: list, start: datetime, end: datetime):
    tomorrow = get_tomorrow(datetime.today())
    day_after_tomorrow = get_tomorrow(tomorrow)
    # check time available
    if not ((tomorrow <= start <= day_after_tomorrow) and (tomorrow <= end <= day_after_tomorrow)):
        logger.error("[aggregator accept] start, end time invalid")
        logger.debug(f"[aggregator accept] start time: {tomorrow <= start <= day_after_tomorrow}")
        logger.debug(f"[aggregator accept] end time: {tomorrow <= end <= day_after_tomorrow}")
        return False
    # GET ALL BIDS, if not accept -> reject
    criteria = (
        DRBidModel.start_time >= tomorrow,
        DRBidModel.start_time < day_after_tomorrow,
        DRBidModel.uuid.in_(uuids),
        DRBidModel.result.is_(None),
    )
    bids = DRBidModel.query.filter(*criteria).all()
    for bid in bids:
        logger.debug(f"[aggregator accept] Accept {bid.uuid}")
        # Accept bids
        bid.acceptor = acceptor
        bid.start_time = start
        bid.end_time = end
        bid.result = True
        bid.status = "已得標"
    try:
        DRBidModel.update(bids)
    except Exception as error:
        logger.error(f"[aggregator accept] error: {error}")
        DRBidModel.rollback()
        return False
    return True


def get_tomorrow(today: datetime):
    tomorrow = today + timedelta(days=1)
    return get_start_of_day(tomorrow)


def get_start_of_day(day: datetime):
    return datetime.combine(day.date(), datetime.min.time())


def get_user_by_account(account: str):
    return User.query.filter_by(account=account).first()


def get_role_account(role: str):
    return User.query.filter_by(role=role).all()


def get_counterpart(executor: str, acceptor: str, logging_role: str, acceptor_role: str):
    return (get_user_by_account(executor)
            if logging_role in ["tpc", acceptor_role]
            else get_user_by_account(acceptor))


def get_dr_volume(start, end):
    criteria = [DRBidModel.start_time == start,
                DRBidModel.end_time == end]
    bids = DRBidModel.query.filter(*criteria).all()
    volume = sum([bid.volume for bid in bids])
    return bids[0].real_volume - volume


def get_cbl(start, end):
    interval = [start, end]
    window = []

    for day in range(5):
        temp = [i - timedelta(days=day) for i in interval]
        criteria = [DRBidModel.start_time == temp[0], DRBidModel.end_time == temp[1]]
        bid = DRBidModel.query.filter(*criteria).first()
        # whether have value
        window.append(bid.real_volume if bid else randint(1, 5))
    return sum(window) / 5
