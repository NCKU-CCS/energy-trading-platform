import uuid
import copy
from datetime import datetime, timedelta

from flask_restful import Resource, reqparse
from loguru import logger

from utils.oauth import auth, g

from .model import DRBidModel, get_role_account, get_counterpart


class DRBid(Resource):
    def __init__(self):
        self._set_get_parser()
        self._set_post_parser()
        self._set_patch_parser()

    def _set_get_parser(self):
        get_temp = reqparse.RequestParser()
        get_temp.add_argument(
            "date",
            type=lambda x: datetime.strptime(x, "%Y-%m-%d"),
            required=False,
            location="args",
            help="date type is %Y-%m-%d",
        )
        get_temp.add_argument(
            "order_method",
            type=str,
            required=False,
            location="args",
            help="order_method is required"
        )
        get_temp.add_argument(
            "per_page",
            type=int,
            required=False,
            location="args",
            default=10,
            help="dr number of per page",
        )
        get_temp.add_argument(
            "page",
            type=int,
            required=False,
            location="args",
            default=1,
            help="which page",
        )

        self.get_parser = copy.deepcopy(get_temp)
        self.aggregator_get_parser = copy.deepcopy(get_temp)
        self.aggregator_get_parser.add_argument(
            "acceptor_role",
            type=str,
            required=True,
            location="args",
            help="acceptor_role argument is required by aggregator",
        )

    def _set_post_parser(self):
        self.post_parser = reqparse.RequestParser()
        self.post_parser.add_argument(
            "start_time",
            type=lambda x: datetime.strptime(x, "%Y-%m-%d"),
            required=True,
            location="json",
            help="start_time is required"
        )
        self.post_parser.add_argument(
            "volume",
            type=float,
            required=True,
            location="json",
            help="volume is required"
        )
        self.post_parser.add_argument(
            "price",
            type=float,
            required=True,
            location="json",
            help="price is required"
        )
        self.post_parser.add_argument(
            "settlement",
            type=float,
            required=True,
            location="json",
            help="settlement is required"
        )
        self.post_parser.add_argument(
            "trading_mode",
            type=int,
            required=True,
            location="json",
            help="trading_mode is required"
        )
        self.post_parser.add_argument(
            "order_method",
            type=str,
            required=True,
            location="json",
            help="order_method is required"
        )

    def _set_patch_parser(self):
        patch_temp = reqparse.RequestParser()
        patch_temp.add_argument(
            "uuid",
            type=lambda x: uuid.UUID(x, version=4),
            required=True,
            location="json",
            help="uuid is required"
        )

        self.patch_parser = copy.deepcopy(patch_temp)
        self.time_patch_parser = copy.deepcopy(patch_temp)
        self.time_patch_parser.add_argument(
            "start_time",
            type=lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S"),
            required=True,
            location="json",
            help="start_time is required",
        )
        self.time_patch_parser.add_argument(
            "end_time",
            type=lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S"),
            required=True,
            location="json",
            help="end_time is required",
        )

    # pylint: disable=R0201
    @auth.login_required
    def get(self):
        logger.info(f"[GET DR]\nUser Account: {g.account}\nUUID: {g.uuid}\n")
        acceptor_role = None
        if g.role == "aggregator":
            args = self.aggregator_get_parser.parse_args()
            logger.info(f"[Get DR]\nacceptor_role: {args['acceptor_role']}")
            acceptor_role = args["acceptor_role"]
        else:
            args = self.get_parser.parse_args()

        # if there is multiple user or aggregator, the code must be refactor
        roles = []
        if g.role == "user":
            roles.append(g.account)
        else:
            accounts = (get_role_account("user")
                        if g.role == acceptor_role
                        else get_role_account("aggregator"))
            roles.extend([user.account for user in accounts])

        criteria = []
        if args["date"]:
            logger.info(f"[GET DR]\ndate: {args['date']}\n")
            criteria.extend([DRBidModel.start_time >= args["date"],
                             DRBidModel.start_time < args["date"] + timedelta(days=1)])
        if args["order_method"]:
            logger.info(f"[GET DR]\norder_method: {args['order_method']}\n")
            criteria.append(DRBidModel.order_method == args["order_method"])

        dr_bids = self.data_table(criteria, roles, args["per_page"], args["page"])
        logger.debug(f"[GET DR]\nnumber of dr_bids: {len(dr_bids)}\n")
        return ([
            {
                "uuid": bid.uuid,
                "executor": bid.executor,
                "acceptor": bid.acceptor,
                "counterpart_name": (
                    get_counterpart(bid.executor, bid.acceptor, g.role, acceptor_role).username
                    if bid.acceptor else None
                ),
                "counterpart_address": (
                    get_counterpart(bid.executor, bid.acceptor, g.role, acceptor_role).address
                    if bid.acceptor else None
                ),
                "start_time": bid.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                "end_time": bid.end_time.strftime("%Y-%m-%d %H:%M:%S") if bid.end_time else None,
                "volume": bid.volume,
                "price": bid.price,
                "settlement": bid.settlement,
                "result": bid.result,
                "status": bid.status,
                "rate": bid.rate,
                "blockchain_url": bid.blockchain_url,
                "trading_mode": bid.trading_mode,
            }
            for bid in dr_bids
        ]
            if dr_bids
            else ("no data on this page", 400)
        )

    @auth.login_required
    def post(self):
        logger.info(f"[Post DR]\nUser Account: {g.account}\nUUID: {g.uuid}\n")
        args = self.post_parser.parse_args()
        args["start_time"] += timedelta(hours=8)
        logger.info(f"[DR]\nstart: {args['start_time']}\nvolume: {args['volume']}\nprice: {args['price']}\
                    \nsettlement: {args['settlement']}\ntrading_mode: {args['trading_mode']}\
                    \norder_method: {args['order_method']}")
        if g.role != 'tpc':
            data = {
                "uuid": uuid.uuid4(),
                "executor": g.account,
                "start_time": args["start_time"],
                "volume": args["volume"],
                "price": args["price"],
                "settlement": args["settlement"],
                "result": False,
                "status": "投標中",
                "trading_mode": args["trading_mode"],
                "order_method": args["order_method"],
            }
            DRBidModel(**data).add()
            return "OK", 200
        return "error", 400

    @auth.login_required
    def patch(self):
        logger.info(f"[PATCH DR]\nUser Account: {g.account}\nUUID: {g.uuid}\n")
        args = self.patch_parser.parse_args()
        logger.info(f"\nuuid: {args['uuid']}\n")
        dr_bid = DRBidModel.query.filter_by(uuid=args["uuid"]).first()
        if dr_bid.executor != g.account:
            args = self.time_patch_parser.parse_args()
            logger.info(f"\nstart_time: {args['start_time']}\nend_time: {args['end_time']}\n")
            dr_bid.start_time = args["start_time"]
            dr_bid.end_time = args["end_time"]
            dr_bid.acceptor = g.account
            dr_bid.result = True
            dr_bid.status = "得標"
        else:
            dr_bid.status = "已投標"
        try:
            DRBidModel.update(dr_bid)
            logger.success("success update dr_bid")
            return "OK", 200
        except Exception:
            logger.error(f"[PATCH DR]\nrole: {g.role}\nuuid: {args['uuid']}\n")
            DRBidModel.rollback()
            return "update error", 400

    def data_table(self, criteria, roles, per_page=10, page=1):
        return (DRBidModel.query.filter(*criteria, DRBidModel.executor.in_(roles))
                                .order_by(DRBidModel.start_time)
                                .offset((page - 1) * per_page)
                                .limit(per_page)
                                .all())
