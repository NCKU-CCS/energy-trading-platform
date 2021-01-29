from datetime import datetime

from flask_script import Command
from loguru import logger

from blockchain.contract import Contract
from blockchain.helper import get_contract_creator, get_event_time
from endpoints.bid.model import BidSubmit, Tenders


class Bid(Command):
    """Logging bid_submit to contract, trigger on 40th minute every hour"""

    def run(self):  # pylint: disable=E0202
        # Trigger time:
        # - every hour at :40

        # Steps:
        # - Get event time ( and corresponding datetime string )
        # - Query bidsumits from users ( 1 for buy, 1 for sell )
        # - Push bidsubmit to blockchain
        # - Change status to Matchresults

        # Get event time
        start_time, _, event_time_str = get_event_time(datetime.now())

        # Query for bidsubmit, by buy and sell
        for bid_type, ordered_field in [('buy', BidSubmit.price.desc()), ('sell', BidSubmit.price.asc())]:
            logger.info(f"[BID SUBMITS]\n {bid_type}, {ordered_field}")

            # get tenders_id and user_id
            for tender in Tenders.query.filter_by(start_time=start_time, bid_type=bid_type).all():
                user = tender.user

                # Bidsubmits for buy/sell
                bidsubmits = (
                    BidSubmit.query.filter_by(tenders_id=tender.uuid, status="投標中").order_by(ordered_field).all()
                )

                # Transform bidsubmits to eth_addr -> {buy -> list, sell -> list}, in appropriate order
                volumes, prices = [], []
                for bid in bidsubmits:
                    volumes.append(int(bid.value))
                    prices.append(int(bid.price))
                logger.info(f"[BID INFO]\n eth_addr: {user.eth_address}\nvolumes: {volumes}\nprices: {prices}\n")

                logger.info(f"USER ID: {user.uuid}")
                contract = Contract(*get_contract_creator())
                result = contract.bid(user.eth_address, event_time_str, bid_type, volumes, prices)
                logger.info(f"Contract Transaction Result: {result}")

                if result:
                    tx_hash = result[0]["transactionHash"]
                    for bid in bidsubmits:
                        bid.status = "已投標"
                        bid.win = 0
                        bid.transaction_hash = tx_hash
                        bid.upload_time = datetime.now()
                        BidSubmit.update(bid)
