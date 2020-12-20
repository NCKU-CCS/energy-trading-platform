import os
import sys
from datetime import datetime

from loguru import logger
from flask_script import Manager

# pylint: disable=C0413
sys.path.insert(0, os.environ.get("WORK_DIR", "./"))  # WORK_DIR is for development
from app import create_app  # noqa: E402
from blockchain.contract import Contract  # noqa: E402
from blockchain.helper import get_contract_creator, get_event_time  # noqa: E402
from endpoints.user.model import User  # noqa: E402
from endpoints.dr.model import DRBidModel  # noqa: E402
from endpoints.bid.model import BidSubmit, MatchResult, Tenders  # noqa: E402

# pylint: enable=C0413


CONFIG = os.environ.get("APP_SETTINGS", "development")
APP = create_app(CONFIG)
MANAGER = Manager(APP)


@MANAGER.command
def bidsubmit():
    """
    Implementation of triggering bid_submit to contract, trigger on 40th minute every hour

    Trigger time:
    - every hour at :40

    Steps:
    - Get event time ( and corresponding datetime string )
    - Query bidsumits from users ( 1 for buy, 1 for sell )
    - Push bidsubmit to blockchain
    - Change status to Matchresults
    """

    # Get event time
    start_time, end_time, event_time_str = get_event_time(datetime.now())

    # Query for bidsubmit, by buy and sell
    for bid_type, ordered_field in [('buy', BidSubmit.price.desc()), ('sell', BidSubmit.price.asc())]:
        logger.info(f"[BID SUBMITS]\n {bid_type}, {ordered_field}")

        # get tenders_id and user_id
        for tender in Tenders.query.filter_by(start_time=start_time, bid_type=bid_type).all():
            user = User.query.filter_by(uuid=tender.user_id).first()

            # Bidsubmits for buy/sell
            bidsubmits = (
                BidSubmit.query.filter_by(tenders_id=tender.uuid).order_by(ordered_field).all()
            )

            # Transform bidsubmits to eth_addr -> {buy -> list, sell -> list}, in appropriate order
            volumes, prices = [], []
            for bid in bidsubmits:
                volumes.append(int(bid.value))
                prices.append(int(bid.price))
            logger.info(f"[BID INFO]\n eth_addr: {user.eth_address}\nvolumes: {volumes}\nprices: {prices}\n")

            logger.info(f"USER ID: {user.uuid}")
            contract = Contract(*get_contract_creator())
            result = contract.bid(
                user.eth_address,
                event_time_str,
                bid_type,
                volumes,
                prices
            )
            logger.info(f"Contract Transaction Result: {result}")

            if result:
                tx_hash = result[0]["transactionHash"]
                data = {
                    "bid_type": bid_type,  # sell or buy
                    "start_time": start_time,
                    "end_time": end_time,
                    "status": "已投標",
                    "win": 0,
                    "bid_value": round(sum(volumes) / len(volumes), 2),
                    "bid_price": round(sum(prices) / len(prices), 2),
                    "transaction_hash": tx_hash,
                    "upload": datetime.now(),
                    "tenders_id": tender.uuid,
                }
                MatchResult(**data).add()


@MANAGER.command
def match():
    """
    Implementation of triggering bid_match to contract, trigger on 45th minute every hour

    Trigger time:
    - hh:45

    Steps:
    - Getting users who had bid for the upcoming event time
    - Trigger match_bids from contract module by passing users and event time
    - Parsing result from contract module and update MatchResult
    """


@MANAGER.command
def execution_and_settlement():
    """
    Implementation of changing MatchResult status to executing and settlement

    Trigger time:
    - hh:00
    """


@MANAGER.command
def done_settlement():
    """
    Implementation of changing MatchResult from in-settlement to done-settlement
    """


@MANAGER.command
def denied_dr_upload():
    """
    Implementation of logging not accepted DR_bids to ethereum smart contract

    Trigger time:
    - every day at 00:10
    """

    # 1. gather dr bids
    dr_bids = (
        DRBidModel.query
        .filter(
            DRBidModel.blockchain_url.is_(None),
            DRBidModel.result.is_(None),
            DRBidModel.start_time < datetime.combine(datetime.now().date(), datetime.min.time())
        )
        .order_by(DRBidModel.start_time)
        .all()
    )

    wanted_columns = ["executor", "acceptor", "start_time", "end_time", "volume", "price", "result"]
    for bid in dr_bids:
        # 2. transform dict to string
        log_text = "".join(
            [
                f"{f'{col}: {bid.__dict__[col]}':32}"
                for col in wanted_columns
            ]
        )
        logger.info(f"[DR Bid Log]\n {log_text}")

        # 3. call for transaction
        contract = Contract(*get_contract_creator())
        result = contract.dr_log(log_text)
        if result:
            tx_hash = result[0]["transactionHash"]
            bid.blockchain_url = f"https://ropsten.etherscan.io/tx/{tx_hash}"
            bid.result = False  # set result to False
            DRBidModel.update(bid)


@MANAGER.command
def accepted_dr_upload():
    """
    Implementation of logging accepted DR_bids to ethereum smart contract

    Trigger time:
    - every minute
    """

    # 1. gather dr bids
    dr_bids = (
        DRBidModel.query
        .filter(
            DRBidModel.blockchain_url.is_(None),
            DRBidModel.result.is_(True),
            DRBidModel.start_time >= datetime.combine(datetime.now().date(), datetime.min.time())
        )
        .order_by(DRBidModel.start_time)
        .all()
    )

    wanted_columns = ["executor", "acceptor", "start_time", "end_time", "volume", "price", "result"]
    for bid in dr_bids:
        # 2. transform dict to string
        log_text = "".join(
            [
                f"{f'{col}: {bid.__dict__[col]}':32}"
                for col in wanted_columns
            ]
        )
        logger.info(f"[DR Bid Log]\n {log_text}")

        # 3. call for transaction
        contract = Contract(*get_contract_creator())
        result = contract.dr_log(log_text)
        if result:
            tx_hash = result[0]["transactionHash"]
            bid.blockchain_url = f"https://ropsten.etherscan.io/tx/{tx_hash}"
            DRBidModel.update(bid)


if __name__ == "__main__":
    MANAGER.run()