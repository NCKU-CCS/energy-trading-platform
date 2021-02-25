import uuid
from datetime import datetime, timedelta

from flask_restful import Resource, reqparse
from loguru import logger

from utils.oauth import auth, g

from .model import DRBidModel, aggregator_accept, user_add_bid, get_user_by_account
from ..user.model import User


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

        date = [DRBidModel.start_time >= args["date"], DRBidModel.start_time < args["date"] + timedelta(days=1)]
        roles = []
        if g.role == "user":
            roles.append(g.account)
        elif g.role == "aggregator":
            accounts = User.query.filter(User.role.in_(["aggregator", "user"])).all()
            roles.extend([user.account for user in accounts])
        elif g.role == "tpc":
            accounts = User.query.filter_by(role="aggregator").all()
            roles.extend([user.account for user in accounts])

        dr_bids = DRBidModel.query.filter(*date,
                                          DRBidModel.executor.in_(roles)).order_by(DRBidModel.start_time).all()
        return [
            {"uuid": bid.uuid, "executor": bid.executor, "volume": bid.volume, "price": bid.price} for bid in dr_bids
        ]

    # pylint: enable=R0201

    # pylint: disable=R0201
    @auth.login_required
    def post(self):
        logger.info(f"[POST DRBid Request]\nUser Account:{g.account}\nUUID:{g.uuid}\n")
        if g.role == "aggregator":
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
            search_args = [
                DRBidModel.start_time >= args["start_date"],
                DRBidModel.end_time < args["end_date"] + timedelta(days=1),
            ]
        elif args["uuid"]:
            logger.info(f"[Get DRBidResult] Query by uuid\nuuids: {args['uuid']}")
            search_args = [DRBidModel.uuid.in_(args["uuid"])]
        else:
            logger.error("[Get DRBidResult] No valid parameters")
            return "parameter is required", 400

        roles = []
        if g.role == "user":
            roles.append(g.account)
        elif g.role == "aggregator":
            accounts = User.query.filter(User.role.in_(["aggregator", "user"])).all()
            roles.extend([user.account for user in accounts])
        elif g.role == "tpc":
            accounts = User.query.filter_by(role="aggregator").all()
            roles.extend([user.account for user in accounts])

        dr_bids = DRBidModel.query.filter(*search_args,
                                          DRBidModel.executor.in_(roles)).order_by(DRBidModel.start_time).all()
        return [
            {
                "uuid": bid.uuid,
                "executor": bid.executor,
                "acceptor": bid.acceptor,
                "counterpart_name": (
                    get_user_by_account(bid.executor).username       # tpc, aggregator in acceptor
                    if g.role == "tpc" or (g.role == "aggregator" and bid.acceptor in accounts)
                    else get_user_by_account(bid.acceptor).username  # user, aggregator in executor
                ),
                "counterpart_address": (
                    get_user_by_account(bid.executor).address        # tpc, aggregator in acceptor
                    if g.role == "tpc" or (g.role == "aggregator" and bid.acceptor in accounts)
                    else get_user_by_account(bid.acceptor).address   # user, aggregator in executor
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
