import os
import sys

from loguru import logger
from flask_script import Manager

# pylint: disable=C0413
sys.path.insert(0, os.environ.get('WORK_DIR', './'))  # WORK_DIR is for development
from app import create_app  # noqa: E402
from blockchain.contract import Contract  # noqa: E402
from endpoints.user.model import User  # noqa: E402
from endpoints.dr.model import DRBidModel  # noqa: E402
# pylint: enable=C0413


CONFIG = os.environ.get('APP_SETTINGS', 'development')
APP = create_app(CONFIG)
MANAGER = Manager(APP)


def get_contract_creator():
    creator = User.query.filter_by(contract_creator=True).first()
    if creator:
        logger.info(
            f"[Get User Request]\nCreator Address:{creator.eth_address}\nEncrypted secret:{creator.eth_secret}"
        )
        return creator.eth_address, creator.eth_secret
    raise LookupError("Sorry, no contractor creator in the database.")


@MANAGER.command
def bid():
    """
    Implementation of triggering bid_submit to contract, trigger on 40th minute every hour

    Trigger time:
    - hh:40

    Steps:
    - Get event time ( and corresponding datetime string )
    - Query bidsumits from users ( 1 for buy, 1 for sell )
    - Push bidsubmit to blockchain
    - Change status to Matchresults
    """


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
def dr_log():
    """
    Implementation of logging DR_bids to ethereum smart contract

    Trigger time:
    - 00:10
    """

    # 1. gather dr bids
    dr_bids = (
        DRBidModel.query.filter_by(blockchain_url=None)
        .order_by(DRBidModel.start_time)
        .all()
    )

    for bid in dr_bids:
        # 2. transform dict to string
        executor = f"executor: {bid.executor}"
        acceptor = f"acceptor: {bid.acceptor}"
        start_time = f"start_time: {bid.start_time.strftime('%Y-%m-%d %H:%M:%S')}"
        end_time = f"end_time: {bid.end_time.strftime('%Y-%m-%d %H:%M:%S')}"
        volume = f"volume: {bid.volume}"
        price = f"price: {bid.price}"
        result = f"result: {bid.result}"

        log_text = "".join((
            f"{executor:32}",
            f"{acceptor:32}",
            f"{start_time:32}",
            f"{end_time:32}",
            f"{volume:32}",
            f"{price:32}",
            f"{result:32}",
        ))

        logger.info(
            f"[DR BID LOG]\n {log_text}"
        )

        # 3. call for transaction
        contract = Contract(*get_contract_creator())
        result = contract.dr_log(log_text)
        tx_hash = result[0]['transactionHash']
        bid.blockchain_url = f"https://ropsten.etherscan.io/tx/{tx_hash}"
        DRBidModel.update(bid)


if __name__ == "__main__":
    MANAGER.run()
