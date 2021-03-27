from datetime import datetime, timedelta

from flask import jsonify, make_response
from flask_restful import Resource, reqparse
from sqlalchemy import func
from loguru import logger

from config import db
from utils.oauth import auth, g
from endpoints.user.model import User
from .model import Tenders, BidSubmit, add_bidsubmit, edit_bidsubmit
from .fake_data import matchresult


class HomePageResource(Resource):
    # pylint: disable=R0201
    @auth.login_required
    def get(self):
        logger.info(f"[Get HomePage Request]\nUser Account:{g.account}\nUUID:{g.uuid}\n")
        # format of response for real time execution info matched bid list
        data = {"buy": {"price": None, "volume": None}, "sell": {"price": None, "volume": None}, "results": []}
        # matched bids are status in one of the ['已得標', '執行中', '結算中', '已結算']
        if g.uuid in [tender.user_id for tender in Tenders.query.all()]:
            results = BidSubmit.query.filter(
                BidSubmit.status.in_(["已得標", "執行中", "結算中", "已結算"]),
                BidSubmit.tenders_id.in_([tender.uuid for tender in Tenders.query.filter_by(user_id=g.uuid).all()]),
            )
            # check current time execution info by further filter the `results` query
            current_time = datetime.now()
            executing_bids = results.filter(
                BidSubmit.start_time <= current_time, BidSubmit.end_time > current_time, BidSubmit.status == "執行中"
            )
            # if `buy` happening, update data object
            buy_bids = executing_bids.filter_by(bid_type="buy").all()
            if buy_bids:
                data["buy"] = {
                    # since buy bids exist, take the first price to data object (same price)
                    "price": buy_bids[0].win_price,
                    # sum of volumes if multiple counterparts exist
                    "volume": sum([bid.win_value for bid in buy_bids]),
                }
            # if `sell` happening, update data object
            sell_bids = executing_bids.filter_by(bid_type="sell").all()
            if sell_bids:
                data["sell"] = {
                    # since sell bids exist, take the first price to data object (same price)
                    "price": sell_bids[0].win_price,
                    # sum of volumes if multiple counterparts exist
                    "volume": sum([bid.win_value for bid in sell_bids]),
                }
            # result of matched bids are based on the order by and limit of results query
            data["results"] = [
                {
                    "date": result.start_time.strftime("%Y/%m/%d"),
                    "time": f'{result.start_time.strftime("%H:00")}-{result.end_time.strftime("%H:00")}',
                    "price": result.win_value,
                    "volume": result.win_price,
                }
                for result in results.order_by(BidSubmit.start_time.desc()).limit(10).all()
            ]
        response = jsonify(data)
        return response

    # pylint: enable=R0201


class MatchResultsResource(Resource):
    # pylint: disable=R0201
    @auth.login_required
    def get(self):
        logger.info(f"[Get MatchResults Request]\nUser Account:{g.account}\nUUID:{g.uuid}\n")

        timdelta_status = {
            "投標中": timedelta(hours=24),
            "已得標": timedelta(hours=23),
            "未得標": -timedelta(hours=1),
            "執行中": timedelta(hours=0),
            "已結算": -timedelta(hours=3),
        }

        # "date": message.start_time.strftime("%Y/%m/%d"),
        # "time": f'{message.start_time.strftime("%H")}:00-{message.end_time.strftime("%H")}:00',

        now = datetime.now()
        # for demo only
        user = User.query.filter_by(uuid=g.uuid).first()
        if user.role == "tpc":
            # tpc will list all data
            total_bids = []
            for value in matchresult.values():
                total_bids.extend(value)
            total_bids.sort(key=lambda item: (item["status"], item["id"]))
            bids = total_bids
        else:
            bids = matchresult[user.username]
        for i, _ in enumerate(bids):
            diff = timdelta_status[bids[i]["status"]]
            event_start_time = now + diff
            event_end_time = event_start_time + timedelta(hours=1)
            bids[i]["date"] = event_start_time.strftime("%Y/%m/%d")
            bids[i]["time"] = f'{event_start_time.strftime("%H")}:00-{event_end_time.strftime("%H")}:00'
            bids[i]["upload"] = event_start_time
        response = jsonify(bids)
        return response

    # pylint: enable=R0201


class BidStatusResource(Resource):
    # pylint: disable=R0201
    @auth.login_required
    def get(self):
        logger.info(f"[Get BidStatus Request]\nUser Account:{g.account}\nUUID:{g.uuid}\n")
        if datetime.today().minute < 40:
            start_time = datetime.today() + timedelta(hours=1)
        else:
            start_time = datetime.today() + timedelta(hours=2)
        start_time = start_time.replace(minute=0).replace(second=0).replace(microsecond=0)
        # filter tenders on given time range
        user_group = Tenders.query.filter(Tenders.start_time == start_time)
        # default response all zeros
        data = {"average_price": 0, "average_volume": 0, "participants": 0}
        # get distinct users count
        distinct_user_count = user_group.distinct(Tenders.user_id).count()
        # if distinct_user_count exists, query for average price and volume base on users
        if distinct_user_count:
            bid_info = (
                db.session.query(
                    (func.sum(BidSubmit.price) / func.count(BidSubmit.price)).label("average_price"),
                    (func.sum(BidSubmit.value) / func.count(BidSubmit.value)).label("average_volume"),
                )
                .filter(BidSubmit.tenders_id.in_([bidder.uuid for bidder in user_group.all()]))
                .first()
            )
            # form the response
            data = {
                "average_price": round(bid_info.average_price, 3),
                "average_volume": round(bid_info.average_volume, 3),
                "participants": distinct_user_count,
            }
        return make_response(jsonify(data))


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
            "bid_type", type=str, required=True, location="json", help="bid_type is required"
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
        self.common_parser.add_argument("value", type=float, required=True, location="json", help="value is required")
        self.common_parser.add_argument("price", type=float, required=True, location="json", help="price is required")

    def _set_get_parser(self):
        self.get_parser = reqparse.RequestParser()
        self.get_parser.add_argument(
            "per_page", type=int, required=True, location="args", help="Get bidsubmit: limit is required"
        )
        self.get_parser.add_argument(
            "page", type=int, required=True, location="args", help="Get bidsubmit: offset is required"
        )
        self.get_parser.add_argument(
            "bid_type", type=str, required=True, location="args", help="Get bidsubmit: bid_type is required"
        )

    def _set_post_parser(self):
        self.post_parser = self.common_parser.copy()

    def _set_put_parser(self):
        self.put_parser = self.common_parser.copy()
        self.put_parser.add_argument(
            "id", type=str, required=True, location="json", help="Put bidsubmit: id is required"
        )

    def _set_delete_parser(self):
        self.delete_parser = reqparse.RequestParser()
        self.delete_parser.add_argument(
            "id", type=str, required=True, location="json", help="Delete bidsubmit: id is required"
        )

    # pylint: disable=R0201
    def _get_user_bid_ids(self, uuid):
        bid_ids = [
            bid.uuid
            for bid in BidSubmit.query.filter(
                BidSubmit.tenders_id.in_([tender.uuid for tender in Tenders.query.filter_by(user_id=uuid).all()])
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

        logger.info(f"[Get BidSubmit Request]\nUser Account:{g.account}\nUUID:{g.uuid}\n")
        bid_query = BidSubmit.query.filter(
            BidSubmit.tenders_id.in_(
                [
                    tender.uuid
                    for tender in Tenders.query.filter(
                        Tenders.user_id == g.uuid,
                        Tenders.start_time >= datetime.today(),
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
            {"data": bids[(offset - 1) * limit : offset * limit], "page": offset, "totalCount": len(bids)}  # noqa: E203
        )
        return response

    @auth.login_required
    def post(self):
        args = self.post_parser.parse_args()
        if args["start_time"] >= datetime.today():
            # insert into db
            logger.info("Insert bid into db")
            if add_bidsubmit(args, g.uuid):
                logger.success("Insert Success")
                return make_response(jsonify({"message": "Accept"}))
            logger.error("Insert Fail")
        logger.error("Bid didn't accept")
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
                return make_response((jsonify({"message": "Reject", "description": "The bid has been closed"}), 400))
            BidSubmit.delete(target)
            return make_response(jsonify({"message": "Accept"}))
        return make_response(jsonify({"message": "Reject", "description": "Invalid ID"}), 400)

    # pylint: enable=R0201
