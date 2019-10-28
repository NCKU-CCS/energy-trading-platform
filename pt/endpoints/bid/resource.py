from flask import jsonify, request
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


class BidSubmitResource(Resource):
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
                    "bid_type": message.bid_type,
                    "start_time": message.start_time.strftime("%Y/%m/%d %H:%M"),
                    "end_time": message.end_time.strftime("%Y/%m/%d %H:%M"),
                    "value": message.value,
                    "price": message.price,
                    "upload_time": message.upload_time,
                }
                for message in BidSubmit.query.filter(
                    BidSubmit.tenders_id.in_(
                        [
                            tender.uuid
                            for tender in Tenders.query.filter_by(user_id=g.uuid).all()
                        ]
                    )
                )
                .order_by(BidSubmit.start_time.desc())
                .all()
            ]
        else:
            bids = []
        response = jsonify(bids)
        return response

    @auth.login_required
    def post(self):
        # Use marshmello to filt input data from body
        # insert into db
        pass

    @auth.login_required
    def put(self):
        # Use marshmello to filt input data from body
        # insert into db
        pass

    @auth.login_required
    def delete(self):
        target_id = str(request.get_json()["id"])
        bid_ids = [
            bid.uuid
            for bid in BidSubmit.query.filter(
                BidSubmit.tenders_id.in_(
                    [
                        tender.uuid
                        for tender in Tenders.query.filter_by(user_id=g.uuid).all()
                    ]
                )
            ).all()
        ]
        if target_id in bid_ids:
            BidSubmit.delete(BidSubmit.query.filter_by(uuid=target_id).first())

    # pylint: enable=R0201
