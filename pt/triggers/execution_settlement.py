from datetime import datetime, timedelta

from flask_script import Command
from loguru import logger

from endpoints.bid.model import BidSubmit
from utils.socketio import socketio
from scripts.test_settlement import simulate_achievement


class ExecSettlement(Command):
    """Changing MatchResult status to executing and settlement"""

    def run(self):  # pylint: disable=E0202
        # Trigger time:
        # - hh:00

        # Bidsubmits to execute
        execution_time = datetime.now()
        bids = (
            BidSubmit.query.filter_by(status="已得標")
            .filter(BidSubmit.start_time <= execution_time, BidSubmit.end_time > execution_time)
            .all()
        )
        for bid in bids:
            bid.status = "執行中"
            bid.update()

        # Bidsubmits to set settling
        settlement_time = execution_time - timedelta(hours=1)
        bids = (
            BidSubmit.query.filter_by(status="執行中")
            .filter(BidSubmit.start_time <= settlement_time, BidSubmit.end_time > settlement_time)
            .all()
        )
        for bid in bids:
            bid.status = "結算中"
            bid.update()


class DoneSettlement(Command):
    """Changing MatchResult from in-settlement to done-settlement"""

    def run(self):  # pylint: disable=E0202
        # Bidsubmits to set settling
        settlement_time = datetime.now() - timedelta(hours=1)
        bids = (
            BidSubmit.query.filter_by(status="結算中")
            .filter(BidSubmit.start_time <= settlement_time, BidSubmit.end_time > settlement_time)
            .all()
        )
        for bid in bids:
            bid.status = "已結算"
            bid.update()


class Settlement(Command):
    """Logging settlement of transaction to smart contract"""

    def run(self):  # pylint: disable=E0202
        # Trigger time:
        # - :10 at that hour

        # emit socket io event
        # simulation then emit
        socketio.emit("transaction", simulate_achievement())
        logger.info("[Emit Settlement Transactions]\nMessage sent")

        # IMPLEMENT ME: true achievement calculation
        # socketio.emit("transaction", `TRUE CALCULATION HERE`)
        # logger.info("[Emit Settlement Transactions]\nMessage sent")
