from datetime import datetime

from flask_script import Command
from loguru import logger

from blockchain.contract import Contract
from blockchain.helper import get_contract_creator
from endpoints.dr.model import DRBidModel


class DRDenied(Command):
    """Logging not accepted DR_bids to ethereum smart contract"""

    def run(self):  # pylint: disable=E0202
        # Trigger time:
        # - every day at 00:10

        # 1. gather dr bids
        dr_bids = (
            DRBidModel.query.filter(
                DRBidModel.blockchain_url.is_(None),
                DRBidModel.result.is_(None),
                DRBidModel.start_time < datetime.combine(datetime.now().date(), datetime.min.time()),
            )
            .order_by(DRBidModel.start_time)
            .all()
        )

        wanted_columns = ["executor", "acceptor", "start_time", "end_time", "volume", "price", "result"]
        for bid in dr_bids:
            # 2. transform dict to string
            log_text = "".join([f"{f'{col}: {bid.__dict__[col]}':32}" for col in wanted_columns])
            logger.info(f"[DR Bid Log]\n {log_text}")

            # 3. call for transaction
            contract = Contract(*get_contract_creator())
            result = contract.dr_log(log_text)
            if result:
                tx_hash = result[0]["transactionHash"]
                bid.blockchain_url = f"https://ropsten.etherscan.io/tx/{tx_hash}"
                bid.result = False  # set result to False
                DRBidModel.update(bid)


class DRAccepted(Command):
    """Logging accepted DR_bids to ethereum smart contract"""

    def run(self):  # pylint: disable=E0202
        # Trigger time:
        # - every minute

        # 1. gather dr bids
        dr_bids = (
            DRBidModel.query.filter(
                DRBidModel.blockchain_url.is_(None),
                DRBidModel.result.is_(True),
                DRBidModel.start_time >= datetime.combine(datetime.now().date(), datetime.min.time()),
            )
            .order_by(DRBidModel.start_time)
            .all()
        )

        wanted_columns = ["executor", "acceptor", "start_time", "end_time", "volume", "price", "result"]
        for bid in dr_bids:
            # 2. transform dict to string
            log_text = "".join([f"{f'{col}: {bid.__dict__[col]}':32}" for col in wanted_columns])
            logger.info(f"[DR Bid Log]\n {log_text}")

            # 3. call for transaction
            contract = Contract(*get_contract_creator())
            result = contract.dr_log(log_text)
            if result:
                tx_hash = result[0]["transactionHash"]
                bid.blockchain_url = f"https://ropsten.etherscan.io/tx/{tx_hash}"
                DRBidModel.update(bid)
