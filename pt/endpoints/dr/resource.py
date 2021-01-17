import uuid
from datetime import datetime, timedelta

from flask_restful import Resource, reqparse
from loguru import logger

from utils.oauth import auth, g

from .model import DRBidModel, aggregator_accept, user_add_bid, get_counterpart


class DRBid(Resource):
    def __init__(self):
        self._set_get_parser()
        self._set_user_post_parser()
        self._set_aggregator_post_parser()

    def _set_get_parser(self):
        self.get_parser = reqparse.RequestParser()
        self.get_parser.add_argument(
            "date",
            type=lambda x: datetime.strptime(x, "%Y-%m-%d"),
            required=True,
            location="args",
            help="date is required",
        )

    def _set_user_post_parser(self):
        self.user_post_parser = reqparse.RequestParser()
        self.user_post_parser.add_argument(
            "volume", type=float, required=True, location="json", help="volume is required"
        )
        self.user_post_parser.add_argument(
            "price", type=float, required=True, location="json", help="price is required"
        )

    def _set_aggregator_post_parser(self):
        self.aggregator_post_parser = reqparse.RequestParser()
        self.aggregator_post_parser.add_argument(
            "start_time",
            type=lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S"),
            required=True,
            location="json",
            help="start_time is required",
        )
        self.aggregator_post_parser.add_argument(
            "end_time",
            type=lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S"),
            required=True,
            location="json",
            help="end_time is required",
        )
        self.aggregator_post_parser.add_argument(
            "uuid", type=str, action="append", required=True, location="json", help="uuid is required"
        )

    # pylint: disable=R0201
    @auth.login_required
    def get(self):
        logger.info(f"[Get DRBid Request]\nUser Account:{g.account}\nUUID:{g.uuid}\n")
        args = self.get_parser.parse_args()
        criteria = [DRBidModel.start_time >= args["date"], DRBidModel.start_time < args["date"] + timedelta(days=1)]
        if not g.is_aggregator:
            # user can only get their own bids
            criteria.append(DRBidModel.executor == g.account)
        dr_bids = DRBidModel.query.filter(*criteria).order_by(DRBidModel.start_time).all()
        return [
            {"uuid": bid.uuid, "executor": bid.executor, "volume": bid.volume, "price": bid.price} for bid in dr_bids
        ]

    # pylint: enable=R0201

    # pylint: disable=R0201
    @auth.login_required
    def post(self):
        logger.info(f"[POST DRBid Request]\nUser Account:{g.account}\nUUID:{g.uuid}\n")
        if g.is_aggregator:
            # aggregator choose bids to accept
            args = self.aggregator_post_parser.parse_args()
            uuids = args["uuid"]
            logger.info(f"[DRBid] start: {args['start_time']}, end:{args['end_time']}\nBids: {uuids}")
            success = aggregator_accept(acceptor=g.account, uuids=uuids, start=args["start_time"], end=args["end_time"])
            if success:
                return "ok"
            return "error", 400
        # user add DR bids
        args = self.user_post_parser.parse_args()
        payload = {"executor": g.account, "volume": args["volume"], "price": args["price"]}
        status = user_add_bid(payload)
        if status:
            return "ok"
        return "error", 400

    # pylint: enable=R0201


class DRBidResult(Resource):
    def __init__(self):
        self._set_get_parser()

    def _set_get_parser(self):
        self.get_parser = reqparse.RequestParser()
        self.get_parser.add_argument(
            "start_date",
            type=lambda x: datetime.strptime(x, "%Y-%m-%d"),
            required=False,
            location="args",
            help="start_date is invalid",
        )
        self.get_parser.add_argument(
            "end_date",
            type=lambda x: datetime.strptime(x, "%Y-%m-%d"),
            required=False,
            location="args",
            help="end_date is invalid",
        )
        self.get_parser.add_argument(
            "uuid",
            type=lambda x: uuid.UUID(x, version=4),
            action="append",
            required=False,
            location="args",
            help="uuid is invalid",
        )

    # pylint: disable=R0201
    @auth.login_required
    def get(self):
        logger.info(f"[Get DRBidResult Request]\nUser Account:{g.account}\nUUID:{g.uuid}\n")
        args = self.get_parser.parse_args()
        if args["start_date"] and args["end_date"]:
            logger.info(
                f"[Get DRBidResult] Query by date\nstart date: {args['start_date']}, end date: {args['end_date']}"
            )
            criteria = [
                DRBidModel.start_time >= args["start_date"],
                DRBidModel.start_time < args["end_date"] + timedelta(days=1),
            ]
        elif args["uuid"]:
            logger.info(f"[Get DRBidResult] Query by uuid\nuuids: {args['uuid']}")
            criteria = [DRBidModel.uuid.in_(args["uuid"])]
        else:
            logger.error("[Get DRBidResult] No valid parameters")
            return "parameter is required", 400

        if not g.is_aggregator:
            # user can only get their bids
            criteria.append(DRBidModel.executor == g.account)

        dr_bids = DRBidModel.query.filter(*criteria).order_by(DRBidModel.start_time).all()
        return [
            {
                "uuid": bid.uuid,
                "executor": bid.executor,
                "acceptor": bid.acceptor,
                "counterpart_name": (
                    get_counterpart(bid.executor).username
                    if g.is_aggregator
                    else get_counterpart(bid.acceptor).username
                ),
                "counterpart_address": (
                    get_counterpart(bid.executor).address
                    if g.is_aggregator
                    else get_counterpart(bid.acceptor).address
                ),
                "start_time": bid.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                "end_time": bid.end_time.strftime("%Y-%m-%d %H:%M:%S") if bid.end_time else None,
                "volume": bid.volume,
                "price": bid.price,
                "result": bid.result,
                "status": bid.status,
                "rate": bid.rate,
                "blockchain_url": bid.blockchain_url,
            }
            for bid in dr_bids
        ]

    # pylint: enable=R0201
