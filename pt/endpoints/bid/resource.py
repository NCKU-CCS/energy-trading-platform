from flask import jsonify
from flask_restful import Resource

from utils.logging import logging
from utils.oauth import auth, g
from .model import MatchResult


class BidsResource(Resource):
    # pylint: disable=R0201
    @auth.login_required
    def get(self):
        logging.info(
            "[Get Bids Request]\nUser Account:%s\nUUID:%s\n" % (g.account, g.uuid)
        )
        bids = [
            {
                "id": message.uuid,
                "time": message.time.strftime("%Y/%m/%d %H:%M"),
                "bid_type": message.bid_type,
                "win": message.win,
                "status": message.status,
                "transaction_hash": message.transaction_hash,
                "upload": message.upload,
                "counterpart": {
                    "name": message.counterpart_name,
                    "address": message.counterpart_address,
                },
                "bids": {"price": message.bid_price, "value": message.win_value},
                "wins": {"price": message.bid_price, "value": message.win_value},
                "achievement": message.achievement,
                "settlement": message.settlement,
            }
            for message in MatchResult.query.all()
        ]
        bids = sorted(bids, key=lambda x: x["upload"], reverse=True)
        response = jsonify(bids)
        return response

    # pylint: enable=R0201
