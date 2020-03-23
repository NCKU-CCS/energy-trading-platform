from datetime import datetime, date, timedelta
from flask import jsonify, make_response
from flask_restful import Resource, reqparse
from sqlalchemy import extract

from utils.logging import logging
from utils.oauth import auth, g
from .model import PowerData
from ..address.model import AMI, History


class PowerDatasResource(Resource):
    def __init__(self):
        # common parser for post and put method
        self._set_get_parser()
        self.power_source = {
            "Demand": (lambda msg: msg.grid, "NetLoad"),
            "ESS": (lambda msg: msg.power_display, "ESS"),
            "EV": (lambda msg: msg.power_display, "EV"),
            "PV": (lambda msg: msg.pac, "PV"),
            "WT": (lambda msg: msg.windgridpower, "WT"),
        }

    def _set_get_parser(self):
        self.get_parser = reqparse.RequestParser()
        self.get_parser.add_argument(
            "time",
            type=str,
            required=False,
            location="args",
            help="Get PowerDatas: time is required",
        )
        self.get_parser.add_argument(
            "per_page",
            type=int,
            required=False,
            location="args",
            help="Get PowerDatas: limit is required",
        )
        self.get_parser.add_argument(
            "page",
            type=int,
            required=False,
            location="args",
            help="Get PowerDatas: offset is required",
        )
        self.get_parser.add_argument(
            "start_time",
            type=str,
            required=False,
            location="args",
            help="Get PowerDatas: time is required",
        )
        self.get_parser.add_argument(
            "end_time",
            type=str,
            required=False,
            location="args",
            help="Get PowerDatas: time is required",
        )
        self.get_parser.add_argument(
            "participant_id",
            type=str,
            required=False,
            location="args",
            help="Get PowerDatas: pariticipant ID is required",
        )

    # pylint: disable=R0201
    @auth.login_required
    def get(self):
        args = self.get_parser.parse_args()
        logging.info(f"[Get Datas Request]\nUser Account:{g.account}\nUUID:{g.uuid}\nIs_Aggregator:{g.is_aggregator}\n")
        if g.is_aggregator is True and args["participant_id"]:
            user_id = args["participant_id"]
        else:
            user_id = g.uuid
        # Data Table Mode
        if args["per_page"] and args["page"]:
            logging.info("[Get Datas Request]:Data Table Mode")
            if args["time"]:
                time = args["time"]
            else:
                time = date.today()
            return self.data_table(args["per_page"], args["page"], time, user_id)
        # Data Charts Mode
        if args["start_time"] and args["end_time"]:
            logging.info("[Get Datas Request]:Data Charts Mode")
            start_time = args["start_time"]
            end_time = args["end_time"]
            # if start time same as end time, default use three days' data
            if start_time == end_time:
                start_time = str(
                    datetime.strptime(start_time, "%Y/%m/%d").date() - timedelta(days=2)
                )
            return self.chart_mode(start_time, end_time, user_id)
        return make_response(jsonify([]))

    # pylint: enable=R0201

    # pylint: disable=R0201
    def data_table(self, limit, offset, time, user_id):
        filter_history = History.query.filter(
            History.time == time,
            History.ami_id == AMI.query.filter_by(user_id=user_id).first().uuid,
        )
        messages = (
            PowerData.query.filter(
                PowerData.history_id.in_([data.uuid for data in filter_history])
            )
            .order_by(PowerData.updated_at.desc())
            .offset((offset - 1) * limit)
            .limit(limit)
            .all()
        )
        total_count = PowerData.query.filter(
            PowerData.history_id.in_([data.uuid for data in filter_history])
        ).count()
        datas = [
            {
                "id": message.uuid,
                "date": message.updated_at.strftime("%Y/%m/%d"),
                "time": message.updated_at.strftime("%H:%M"),
                "data_type": self.power_source[message.data_type][1],
                "power_display": self.power_source[message.data_type][0](message),
                "address": f"https://thetangle.org/transaction/{message.address}",
            }
            for message in messages
        ]
        return make_response(
            jsonify({"data": datas, "page": offset, "totalCount": total_count})
        )

    # pylint: enable=R0201

    # pylint: disable=R0201
    def chart_mode(self, start_time, end_time, user_id):
        filter_history = History.query.filter(
            History.time >= start_time,
            History.time <= end_time,
            History.ami_id == AMI.query.filter_by(user_id=user_id).first().uuid,
        )
        messages = (
            PowerData.query.filter(
                PowerData.history_id.in_([data.uuid for data in filter_history]),
                # Hourly data every two hours
                extract("minute", PowerData.updated_at) == "00",
                extract("hour", PowerData.updated_at).in_(
                    ["%02d" % i for i in range(0, 25, 2)]
                ),
            )
            .order_by(PowerData.updated_at)
            .all()
        )
        charts_datas = {}
        for message in messages:
            data_time = message.updated_at.strftime("%Y/%m/%d %H:%M")
            if data_time not in charts_datas:
                charts_datas[data_time] = {}
                charts_datas[data_time]["name"] = data_time
            charts_datas[data_time][message.data_type] = self.power_source[
                message.data_type
            ][0](message)
        return make_response(
            jsonify(sorted(list(charts_datas.values()), key=lambda item: item["name"]))
        )

    # pylint: enable=R0201
