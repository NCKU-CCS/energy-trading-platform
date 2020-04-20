from datetime import datetime, timedelta

from flask import jsonify, make_response
from flask_restful import Resource, reqparse
from sqlalchemy import extract
from loguru import logger

from utils.oauth import auth, g
from .model import PowerData, Demand, PV, EV, WT, ESS
from ..user.model import User


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
            help="Get PowerData: time is required",
        )
        self.get_parser.add_argument(
            "per_page",
            type=int,
            required=False,
            location="args",
            help="Get PowerData: limit is required",
        )
        self.get_parser.add_argument(
            "page",
            type=int,
            required=False,
            location="args",
            help="Get PowerData: offset is required",
        )
        self.get_parser.add_argument(
            "start_time",
            type=str,
            required=False,
            location="args",
            help="Get PowerData: time is required",
        )
        self.get_parser.add_argument(
            "end_time",
            type=str,
            required=False,
            location="args",
            help="Get PowerData: time is required",
        )
        self.get_parser.add_argument(
            "summary_date",
            type=str,
            required=False,
            location="args",
            help="Get PowerData: summary date is required",
        )
        self.get_parser.add_argument(
            "participant_id",
            type=str,
            required=False,
            location="args",
            help="Get PowerData: pariticipant ID is required",
        )

    # pylint: disable=R0201
    @auth.login_required
    def get(self):
        args = self.get_parser.parse_args()
        logger.info(
            f"[Get PowerData Request]\nUser Account:{g.account}\nUUID:{g.uuid}\nIs_Aggregator:{g.is_aggregator}\n"
        )
        # Account comfirmation by UUID
        if g.is_aggregator is True and args["participant_id"]:
            user = User.query.filter_by(uuid=args["participant_id"]).first()
            if user:
                field = user.account
            else:
                field = g.account
        else:
            field = g.account
        # Data Table Mode
        if args["per_page"] and args["page"]:
            logger.info("[Get PowerData Request]:Data Table Mode")
            if args["time"]:
                time = datetime.strptime(args["time"], "%Y/%m/%d")
            else:
                time = datetime.combine(datetime.today(), datetime.min.time())
            return self.data_table(args["per_page"], args["page"], time, field)
        # Data Charts Mode
        if args["start_time"] and args["end_time"]:
            logger.info("[Get PowerData Request]:Data Charts Mode")
            start_time = datetime.strptime(args["start_time"], "%Y/%m/%d")
            end_time = datetime.strptime(args["end_time"], "%Y/%m/%d")
            # if start time same as end time, default use three days' data
            if start_time == end_time:
                start_time -= timedelta(days=2)
            return self.chart_mode(start_time, end_time, field)
        # Day Summary Mode
        if args["summary_date"]:
            logger.info("[Get PowerData Request]:Day Summary Mode")
            start_time = datetime.strptime(args["summary_date"], "%Y/%m/%d")
            end_time = start_time + timedelta(days=1)
            return self.summary_mode(start_time, end_time, field)
        return make_response(jsonify([]))

    # pylint: enable=R0201

    # pylint: disable=R0201
    def data_table(self, limit, offset, time, field):
        messages = (
            PowerData.query.filter(
                PowerData.field == field,
                PowerData.updated_at >= time,
                PowerData.updated_at <= time + timedelta(days=1),
            )
            .order_by(PowerData.updated_at.desc())
            .offset((offset - 1) * limit)
            .limit(limit)
            .all()
        )
        total_count = PowerData.query.filter(
            PowerData.field == field,
            PowerData.updated_at >= time,
            PowerData.updated_at <= time + timedelta(days=1),
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
    def chart_mode(self, start_time, end_time, field):
        messages = (
            PowerData.query.filter(
                PowerData.field == field,
                PowerData.updated_at >= start_time,
                PowerData.updated_at <= end_time,
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
        data = sorted(list(charts_datas.values()), key=lambda item: item["name"])
        for entry in data:
            entry['Generate'] = round(entry['ESS'] + entry['EV'] + entry['PV'] + entry['WT'], 3)
            entry['Consume'] = round(entry['Demand'] - entry['Generate'], 3)
        return make_response(jsonify(data))

    # pylint: enable=R0201

    # pylint: disable=R0201
    def summary_mode(self, start_time, end_time, field):
        # Demand sum
        demand_data = Demand.query.filter(
            Demand.uuid.in_(
                [data.uuid for data in PowerData.query.filter(
                    PowerData.updated_at >= start_time,
                    PowerData.updated_at < end_time,
                    PowerData.field == field,
                    PowerData.data_type == 'Demand'
                ).all()]
            )
        ).all()
        # PV sum
        pv_data = PV.query.filter(
            PV.uuid.in_(
                [data.uuid for data in PowerData.query.filter(
                    PowerData.updated_at >= start_time,
                    PowerData.updated_at < end_time,
                    PowerData.field == field,
                    PowerData.data_type == 'PV'
                ).all()]
            )
        ).all()
        # EV sum
        ev_data = EV.query.filter(
            EV.uuid.in_(
                [data.uuid for data in PowerData.query.filter(
                    PowerData.updated_at >= start_time,
                    PowerData.updated_at < end_time,
                    PowerData.field == field,
                    PowerData.data_type == 'EV'
                ).all()]
            )
        ).all()
        # WT sum
        wt_data = WT.query.filter(
            WT.uuid.in_(
                [data.uuid for data in PowerData.query.filter(
                    PowerData.updated_at >= start_time,
                    PowerData.updated_at < end_time,
                    PowerData.field == field,
                    PowerData.data_type == 'WT'
                ).all()]
            )
        ).all()
        # ESS sum
        ess_data = ESS.query.filter(
            ESS.uuid.in_(
                [data.uuid for data in PowerData.query.filter(
                    PowerData.updated_at >= start_time,
                    PowerData.updated_at < end_time,
                    PowerData.field == field,
                    PowerData.data_type == 'ESS'
                ).all()]
            )
        ).all()
        data = {
            "Demand": round(sum([d.grid for d in demand_data]) / 60, 3) if demand_data else 0,
            "WT": round(sum([d.windgridpower for d in wt_data]) / 60, 3) if wt_data else 0,
            "PV": round(sum([d.pac for d in pv_data]) / 60, 3) if pv_data else 0,
            "EV": round(sum([d.power_display for d in ev_data]) / 60, 3) if ev_data else 0,
            "ESS": round(sum([d.power_display for d in ess_data]) / 60, 3) if ess_data else 0
        }
        # Add Power comsumption field
        consume = round(data['Demand'] - data['WT'] - data['PV'] - data['EV'] - data['ESS'], 3)
        data["Consume"] = consume
        return make_response(jsonify(data))

    # pylint: enable=R0201
