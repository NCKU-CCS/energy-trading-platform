import os
import sys
from datetime import datetime, time, timedelta

from loguru import logger

# pylint: disable=C0413
sys.path.insert(0, os.environ.get("WORK_DIR", "./"))  # WORK_DIR is for development
from endpoints.user.model import User  # noqa: E402
from endpoints.bid.model import BidSubmit  # noqa: E402

# pylint: enable=C0413


################
# event helper #
################


def get_contract_creator():
    creator = User.query.filter_by(contract_creator=True).first()
    if creator:
        logger.info(f"[Get User Request]\nCreator Address:{creator.eth_address}\nEncrypted secret:{creator.eth_secret}")
        return creator.eth_address, creator.eth_secret
    raise LookupError("Sorry, no contractor creator in the database.")


def get_event_time(time_now):
    start_time = time_now + timedelta(hours=1)  # get bid event time
    start_time = datetime.combine(start_time.date(), time(start_time.hour, 0))  # truncate min and sec of event_time
    end_time = start_time + timedelta(hours=1)
    event_time_str = start_time.strftime("%Y-%m-%d %H")  # make time string for contract
    return start_time, end_time, event_time_str


def get_execution_time(time_now):
    return datetime.combine(time_now.date(), time(time_now.hour, 0))


#########################
# Match helper function #
#########################


def get_bidsubmits(start_time):
    bids = {"buy": [], "sell": []}
    for bid_type, ordered_field in [('buy', BidSubmit.price.desc()), ('sell', BidSubmit.price.asc())]:
        logger.info(f"[MATCH | BID SUBMITS]\n {bid_type}, {ordered_field}")

        # get tenders_id and user_id
        bidsubmits = (
            BidSubmit.query.filter_by(start_time=start_time, bid_type=bid_type, status="已投標")
            .order_by(ordered_field)
            .all()
        )

        biddings = (
            [[bidsubmit.value, bidsubmit.price] for bidsubmit in bidsubmits]
        )
        bids[bid_type] = biddings
    return bids["buy"], bids["sell"]


def get_matched_bidsubmits(start_time, win_price):
    bids = {"buy": [], "sell": []}
    conditions = [
        ('buy', BidSubmit.price.desc(), BidSubmit.price >= win_price),
        ('sell', BidSubmit.price.asc(), BidSubmit.price <= win_price),
    ]
    for bid_type, ordered_field, filter_price in conditions:
        logger.info(f"[MATCH | BID SUBMITS]\n {bid_type}, {ordered_field}")

        # get tenders_id and user_id
        bidsubmits = (
            BidSubmit.query.filter_by(start_time=start_time, bid_type=bid_type, status="已投標")
            .filter(filter_price)
            .order_by(ordered_field)
            .all()
        )
        bids[bid_type] = bidsubmits
    return bids["buy"], bids["sell"]


def accumulate_bids(buy_bids, sell_bids):
    """
    Description:
        Accumulate buys and sells volume value for demand-supply list
    Arguments:
        buy_bids - buyers' bidsubmits. Index:(volume, price)
        sell_bids - sellers' bidsubmits. Index:(volume, price)
    """

    for i in range(1, len(sell_bids)):
        sell_bids[i][0] += sell_bids[i - 1][0]

    for i in range(1, len(buy_bids)):
        buy_bids[i][0] += buy_bids[i - 1][0]

    return buy_bids, sell_bids


def get_base_volumes(buy_bids, sell_bids):
    """
    Description:
        Get the base volumes for all the buys and sells.
    Arguments:
        buy_bids - buyers' bidsubmits. Index:(volume, price)
        sell_bids - sellers' bidsubmits. Index:(volume, price)
    """

    set_buy = {buy[0] for buy in buy_bids}
    set_sell = {sell[0] for sell in sell_bids}
    base_volumes = list(set_buy.union(set_sell))
    base_volumes.sort()
    return base_volumes


def get_matched_point(buy_bids, sell_bids):
    """
    Description:
        Make buys and sells have same volume axis (base on `get_base_volumes`)
    Arguments:
        buy_bids - buyers' bidsubmits. Index:(volume, price)
        sell_bids - sellers' bidsubmits. Index:(volume, price)
    """

    base_volumes = get_base_volumes(*accumulate_bids(buy_bids, sell_bids))
    buy_bids.insert(0, [0, 0])
    sell_bids.insert(0, [0, 0])

    matched_price = 0
    matched_volume = 0
    matched = False
    for volume in base_volumes:
        # price buy
        for i in range(1, len(buy_bids)):
            if buy_bids[i - 1][0] < volume <= buy_bids[i][0]:
                price_buy = buy_bids[i][1]
                break
        else:
            price_buy = buy_bids[-1][1]

        # volume sell
        for i in range(1, len(sell_bids)):
            if sell_bids[i - 1][0] < volume <= sell_bids[i][0]:
                price_sell = sell_bids[i - 1][1]
                break
        else:
            price_sell = sell_bids[-1][1]

        if price_buy <= price_sell:
            matched = True
            break

        matched_price = price_sell
        matched_volume = volume

    if matched:
        return matched_volume, matched_price
    return None


def generate_success_matchresult(start_time, tx_hash, win_value, win_price):
    buy_bidsubmits, sell_bidsubmits = get_matched_bidsubmits(start_time, win_price)
    buy_total = sum([bid.value for bid in buy_bidsubmits])
    sell_total = sum([bid.value for bid in sell_bidsubmits])

    while buy_bidsubmits and sell_bidsubmits:
        buy_volume = round(win_value * (buy_bidsubmits[-1].value / buy_total), 2)
        sell_volume = round(win_value * (sell_bidsubmits[-1].value / sell_total), 2)
        if buy_volume > sell_volume:
            # update both bidsubmit for sell and buy
            update_bidsubmit(buy_bidsubmits[-1], sell_bidsubmits[-1], tx_hash, sell_volume, win_price)

            # clone all columns except uuid
            data = buy_bidsubmits[-1].__dict__
            if data.pop("uuid", None):
                data.pop("_sa_instance_state", None)
                data["value"] -= sell_volume
                buy_bidsubmits[-1] = BidSubmit.add(**data)

            # sell allocated, pop the bid from behind
            sell_bidsubmits.pop()
        elif buy_volume == sell_volume:
            # update both bidsubmit for sell and buy
            update_bidsubmit(buy_bidsubmits[-1], sell_bidsubmits[-1], tx_hash, sell_volume, win_price)

            # sell and buy both allocated, pop them from behind
            buy_bidsubmits.pop()
            sell_bidsubmits.pop()
        else:
            # update both bidsubmit for sell and buy
            update_bidsubmit(buy_bidsubmits[-1], sell_bidsubmits[-1], tx_hash, buy_volume, win_price)

            # clone all columns except uuid
            data = sell_bidsubmits[-1].__dict__
            if data.pop("uuid", None):
                data.pop("_sa_instance_state", None)
                data["value"] -= buy_volume
                sell_bidsubmits[-1] = BidSubmit.add(**data)
            buy_bidsubmits.pop()


def update_bidsubmit(buy, sell, tx_hash, value, price):
    buyer = buy.tenders.user
    seller = sell.tenders.user

    # buy_bidsubmit
    buy.win = 1
    buy.status = "已得標"
    buy.counterpart_name = seller.username
    buy.counterpart_address = seller.address
    buy.win_value = value
    buy.win_price = price
    buy.achievement = 0
    buy.settlement = 0
    buy.transaction_hash = tx_hash
    buy.upload_time = datetime.now()
    buy.update()

    # sell_bidsubmit
    sell.win = 1
    sell.status = "已得標"
    sell.counterpart_name = buyer.username
    sell.counterpart_address = buyer.address
    sell.win_value = value
    sell.win_price = price
    sell.achievement = 0
    sell.settlement = 0
    sell.transaction_hash = tx_hash
    sell.upload_time = datetime.now()
    sell.update()


def generate_denied_matchresult(start_time, tx_hash):
    matchresults = (
        BidSubmit.query.filter_by(start_time=start_time, status="已投標")
        .all()
    )

    for result in matchresults:
        result.status = "未得標"
        result.upload_time = datetime.now()
        result.tx_hash = tx_hash
        result.win = 0
        result.update()
