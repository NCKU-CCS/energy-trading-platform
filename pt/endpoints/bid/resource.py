from flask import jsonify
from flask_restful import Resource

from utils.logging import logging
from utils.oauth import auth, g
from .model import Tenders, MatchResult, BidSubmit


class MatchResultsResource(Resource):
    # pylint: disable=R0201
    @auth.login_required
    def get(self):
        logging.info(
            "[Get MatchResults Request]\nUser Account:%s\nUUID:%s\n"
            % (g.account, g.uuid)
        )
        if g.uuid in [tender.user_id for tender in Tenders.query.all()]:
            bids = [
                {
                    "id": message.uuid,
                    "start_time": message.start_time.strftime("%Y/%m/%d %H:%M"),
                    "end_time": message.end_time.strftime("%Y/%m/%d %H:%M"),
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
                for message in MatchResult.query.filter(
                    MatchResult.tenders_id.in_(
                        [
                            tender.uuid
                            for tender in Tenders.query.filter_by(user_id=g.uuid).all()
                        ]
                    )
                )
                .order_by(MatchResult.start_time.desc())
                .all()
            ]
        else:
            bids = []
        response = jsonify(bids)
        return response

    # pylint: enable=R0201
