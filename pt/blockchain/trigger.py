import os
import sys

from loguru import logger
from flask_script import Manager

# pylint: disable=C0413
sys.path.insert(0, os.environ.get('WORK_DIR', './'))  # WORK_DIR is for development
from app import create_app  # noqa: E402
from blockchain.contract import Contract  # noqa: E402
from endpoints.user.model import User  # noqa: E402
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


# Trigger at :40
@MANAGER.command
def bid():
    """
    Implementation of triggering bid_submit to contract, trigger on 40th minute every hour

    Steps:
    - Get event time ( and corresponding datetime string )
    - Query bidsumits from users ( 1 for buy, 1 for sell )
    - Push bidsubmit to blockchain
    - Change status to Matchresults
    """


# Trigger at :45
@MANAGER.command
def match():
    """
    Implementation of triggering bid_match to contract, trigger on 45th minute every hour

    Steps:
    - Getting users who had bid for the upcoming event time
    - Trigger match_bids from contract module by passing users and event time
    - Parsing result from contract module and update MatchResult
    """


# Trigger at :00
@MANAGER.command
def execution_and_settlement():
    """
    Implementation of changing MatchResult status to executing and settlement
    """


@MANAGER.command
def done_settlement():
    """
    Implementation of changing MatchResult from in-settlement to done-settlement
    """


@MANAGER.command
def dr_log():
    """
    Log DR bid to ethereum
    """

    # 1. gather dr bid
    # 2. transfer data to string

    # 3. call for transaction
    example = "executor:1 acceptor:2"
    contract = Contract(*get_contract_creator())
    result = contract.dr_log(example)
    print(result)


if __name__ == "__main__":
    MANAGER.run()
