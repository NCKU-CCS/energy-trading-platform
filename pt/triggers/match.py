from datetime import datetime

from flask_script import Command
from loguru import logger

from blockchain.contract import Contract
from blockchain.helper import (
    get_bidsubmits,
    get_contract_creator,
    get_event_time,
    get_matched_point,
    generate_success_matchresult,
    generate_denied_matchresult,
)


class Match(Command):
    """Triggering bid_match to contract, trigger on 45th minute every hour"""

    def run(self):  # pylint: disable=E0202
        # Trigger time:
        # - every hour at hh:45

        # Steps:
        # - Getting users who had bid for the upcoming event time
        # - Trigger match_bids from contract module by passing users and event time
        # - Parsing result from contract module and update MatchResult

        start_time, _, event_time_str = get_event_time(datetime.now())

        buy_bids, sell_bids = get_bidsubmits(start_time)

        matched = get_matched_point(buy_bids, sell_bids)

        if matched:
            win_volume, win_price = matched

            # upload to smart contract (use dr_log method)
            # transform dict to string
            match_dict = {"event_time": event_time_str, "matched price": win_price, "matched_volume": win_volume}
            log_text = "".join([f"{f'{key}: {value}':32}" for key, value in match_dict.items()])
            logger.info(f"[Match bids log]\n {log_text}")

            # call for transaction
            contract = Contract(*get_contract_creator())
            result = contract.dr_log(log_text)  # use dr_log temporary
            if result:
                tx_hash = result[0]["transactionHash"]
                logger.info(f"Contract Transaction Result: {result}")
                generate_success_matchresult(start_time, tx_hash, win_volume, win_price)
                generate_denied_matchresult(start_time, tx_hash)
