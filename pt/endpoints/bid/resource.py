from datetime import datetime

from flask import jsonify, make_response
from flask_restful import Resource, reqparse
from loguru import logger

from utils.oauth import auth, g
from .model import Tenders, MatchResult, BidSubmit, add_bidsubmit, edit_bidsubmit


class MatchResultsResource(Resource):
    # pylint: disable=R0201
    @auth.login_required
    def get(self):
        logger.info(
            f"[Get MatchResults Request]\nUser Account:{g.account}\nUUID:{g.uuid}\n"
        )
        if g.uuid in [tender.user_id for tender in Tenders.query.all()]:
            bids = [
                {
                    "id": message.uuid,
                    "date": message.start_time.strftime("%Y/%m/%d"),
                    "time": f'{message.start_time.strftime("%H")}:00-{message.end_time.strftime("%H")}:00',
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
    def __init__(self):
        # common parser for post and put method
        self._set_common_parser()
        # get bidsubmit
        self._set_get_parser()
        # add bidsubmit
        self._set_post_parser()
        # edit bidsubmit
        self._set_put_parser()
        # delete bidsubmit
        self._set_delete_parser()

    def _set_common_parser(self):
        self.common_parser = reqparse.RequestParser()
        self.common_parser.add_argument(
            "bid_type",
            type=str,
            required=True,
            location="json",
            help="bid_type is required",
        )
        self.common_parser.add_argument(
            "start_time",
            type=lambda x: datetime.strptime(x, "%Y/%m/%d %H"),
            required=True,
            location="json",
            help="start_time is required",
        )
        self.common_parser.add_argument(
            "end_time",
            type=lambda x: datetime.strptime(x, "%Y/%m/%d %H"),
            required=True,
            location="json",
            help="end_time is required",
        )
        self.common_parser.add_argument(
            "value",
            type=float,
            required=True,
            location="json",
            help="value is required",
        )
        self.common_parser.add_argument(
            "price",
            type=float,
            required=True,
            location="json",
            help="price is required",
        )

    def _set_get_parser(self):
        self.get_parser = reqparse.RequestParser()
        self.get_parser.add_argument(
            "per_page",
            type=int,
            required=True,
            location="args",
            help="Get bidsubmit: limit is required",
        )
        self.get_parser.add_argument(
            "page",
            type=int,
            required=True,
            location="args",
            help="Get bidsubmit: offset is required",
        )
        self.get_parser.add_argument(
            "bid_type",
            type=str,
            required=True,
            location="args",
            help="Get bidsubmit: bid_type is required",
        )

    def _set_post_parser(self):
        self.post_parser = self.common_parser.copy()

    def _set_put_parser(self):
        self.put_parser = self.common_parser.copy()
        self.put_parser.add_argument(
            "id",
            type=str,
            required=True,
            location="json",
            help="Put bidsubmit: id is required",
        )

    def _set_delete_parser(self):
        self.delete_parser = reqparse.RequestParser()
        self.delete_parser.add_argument(
            "id",
            type=str,
            required=True,
            location="json",
            help="Delete bidsubmit: id is required",
        )

    # pylint: disable=R0201
    def _get_user_bid_ids(self, uuid):
        bid_ids = [
            bid.uuid
            for bid in BidSubmit.query.filter(
                BidSubmit.tenders_id.in_(
                    [
                        tender.uuid
                        for tender in Tenders.query.filter_by(user_id=uuid).all()
                    ]
                )
            ).all()
        ]
        return bid_ids

    # pylint: enable=R0201

    # pylint: disable=R0201
    @auth.login_required
    def get(self):
        args = self.get_parser.parse_args()
        limit = args["per_page"]
        offset = args["page"]

        logger.info(
            f"[Get BidSubmit Request]\nUser Account:{g.account}\nUUID:{g.uuid}\n"
        )
        bid_query = BidSubmit.query.filter(
            BidSubmit.tenders_id.in_(
                [
                    tender.uuid
                    for tender in Tenders.query.filter(
                        Tenders.user_id == g.uuid,
                        Tenders.start_time >= datetime.utcnow(),
                        Tenders.bid_type == args["bid_type"],
                    ).all()
                ]
            )
        )
        # buy prices is in high to low order
        if args["bid_type"] == "buy":
            bid_queryset = bid_query.order_by(BidSubmit.start_time, BidSubmit.price.desc()).all()
        # sell prices is in low to high order
        elif args["bid_type"] == "sell":
            bid_queryset = bid_query.order_by(BidSubmit.start_time, BidSubmit.price.asc()).all()
        bids = [
            {
                "id": message.uuid,
                "bid_type": message.bid_type,
                "start_time": message.start_time.strftime("%Y/%m/%d %H"),
                "end_time": message.end_time.strftime("%Y/%m/%d %H"),
                "volume": message.value,
                "price": message.price,
                "upload_time": message.upload_time,
                "date": message.start_time.strftime("%Y/%m/%d"),
                "time": int(message.start_time.strftime("%H")),
                "total_price": message.value * message.price,
            }
            for message in bid_queryset
        ]
        response = jsonify(
            {
                "data": bids[(offset - 1) * limit : offset * limit],  # noqa: E203
                "page": offset,
                "totalCount": len(bids),
            }
        )
        return response

    @auth.login_required
    def post(self):
        args = self.post_parser.parse_args()
        if args["start_time"] >= datetime.today():
            # insert into db
            if add_bidsubmit(args, g.uuid):
                return make_response(jsonify({"message": "Accept"}))
        return make_response(jsonify({"message": "Reject"}))

    @auth.login_required
    def put(self):
        args = self.put_parser.parse_args()
        if args["start_time"] >= datetime.today():
            bid_ids = self._get_user_bid_ids(g.uuid)
            if args["id"] in bid_ids:
                # insert into db
                if edit_bidsubmit(args, g.uuid):
                    return make_response(jsonify({"message": "Accept"}))
        return make_response(jsonify({"message": "Reject"}))

    @auth.login_required
    def delete(self):
        args = self.delete_parser.parse_args()
        target_id = args["id"]
        bid_ids = self._get_user_bid_ids(g.uuid)
        if target_id in bid_ids:
            target = BidSubmit.query.filter_by(uuid=target_id).first()
            if target.start_time < datetime.today():
                return make_response(
                    (
                        jsonify(
                            {
                                "message": "Reject",
                                "description": "The bid has been closed",
                            }
                        ),
                        400,
                    )
                )
            BidSubmit.delete(target)
            return make_response(jsonify({"message": "Accept"}))
        return make_response(
            jsonify({"message": "Reject", "description": "Invalid ID"}), 400
        )

    # pylint: enable=R0201
