from datetime import datetime, timedelta

from flask import jsonify, make_response
from flask_restful import Resource, reqparse
from sqlalchemy import cast, func, DATE
from sqlalchemy.dialects.postgresql import INTERVAL
from sqlalchemy.sql.functions import concat
from loguru import logger

from utils.oauth import auth, g
from config import db
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
        # Common powerdata type object for chart and summary mode
        self.powerdata_datatype = {
            "Demand": {"model": Demand, "field": Demand.grid},
            "PV": {"model": PV, "field": PV.pac},
            "EV": {"model": EV, "field": EV.power_display},
            "ESS": {"model": ESS, "field": ESS.power_display},
            "WT": {"model": WT, "field": WT.windgridpower},
        }

    def _set_get_parser(self):
        self.get_parser = reqparse.RequestParser()
        self.get_parser.add_argument(
            "time", type=str, required=False, location="args", help="Get PowerData: time is required"
        )
        self.get_parser.add_argument(
            "per_page", type=int, required=False, location="args", help="Get PowerData: limit is required"
        )
        self.get_parser.add_argument(
            "page", type=int, required=False, location="args", help="Get PowerData: offset is required"
        )
        self.get_parser.add_argument(
            "chart_date", type=str, required=False, location="args", help="Get PowerData: chart date is required"
        )
        self.get_parser.add_argument(
            "summary_date", type=str, required=False, location="args", help="Get PowerData: summary date is required"
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
            f"[Get PowerData Request]\nUser Account:{g.account}\nUUID:{g.uuid}\nRole:{g.role}\n"
        )
        # Account confirmation by UUID
        # Default account
        field = g.account
        if g.role == "aggregator" and args["participant_id"]:
            # if participant_id is present, replace field name by requested account
            user = User.query.filter_by(uuid=args["participant_id"]).first()
            if user:
                field = user.account
        # Data Table Mode
        if args["per_page"] and args["page"]:
            logger.info(f"[Get PowerData Request]:Data Table Mode\nField:{field}")
            if args["time"]:
                time = datetime.strptime(args["time"], "%Y/%m/%d")
            else:
                time = datetime.combine(datetime.today(), datetime.min.time())
            return self.data_table(args["per_page"], args["page"], time, field)
        # Data Charts Mode
        if args["chart_date"]:
            logger.info(f"[Get PowerData Request]:Data Charts Mode\nField:{field}")
            chart_date = datetime.strptime(args["chart_date"], "%Y/%m/%d")
            start_time = chart_date - timedelta(days=6)
            end_time = chart_date
            return self.chart_mode(start_time, end_time, field)
        # Day Summary Mode
        if args["summary_date"]:
            logger.info(f"[Get PowerData Request]:Day Summary Mode\nField:{field}")
            start_time = datetime.strptime(args["summary_date"], "%Y/%m/%d")
            end_time = start_time + timedelta(days=1)
            return self.summary_mode(start_time, end_time, field)
        return make_response(jsonify([]))

    # pylint: enable=R0201

    # pylint: disable=R0201
    def data_table(self, limit, offset, time, field):
        # query for all powerdata within the day
        powerdata = PowerData.query.filter(
            PowerData.field == field,
            PowerData.updated_at.between(time, time + timedelta(days=1)),
        )
        # get requested powerdata by setting order, offset, and limit based on above query
        messages = (
            powerdata.order_by(PowerData.updated_at.desc())
            .offset((offset - 1) * limit)
            .limit(limit)
            .all()
        )
        # building the response from messages
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
        return make_response(jsonify({"data": datas, "page": offset, "totalCount": powerdata.count()}))

    # pylint: enable=R0201

    # pylint: disable=R0201
    def chart_mode(self, start_time, end_time, field):
        # referencing the powerdata_datatype object
        powerdata_datatype = self.powerdata_datatype
        # gather 7 days powerdata by traversing the power_datatype objects
        powerdata = {}
        for data_type in powerdata_datatype:
            # the kW record per minute should divide by 60 to convert to kWh
            powerdata[data_type] = (
                db.session.query(
                    cast(
                        powerdata_datatype[data_type]["model"].updated_at
                        + func.cast(concat(8, " HOURS"), INTERVAL),
                        DATE,
                    ).label("date"),
                    (func.sum(powerdata_datatype[data_type]["field"]) / 60).label(
                        "sum"
                    ),
                )
                .filter(
                    powerdata_datatype[data_type]["model"].updated_at.between(
                        start_time, end_time
                    ),
                    powerdata_datatype[data_type]["model"].field == field,
                )
                .group_by("date")
                .order_by("date")
                .all()
            )
        # distribute data to response format
        powerdata_list = []
        for i in range(len(powerdata['Demand'])):
            data = {
                power_type: round(powerdata[power_type][i].sum, 3) if i < len(powerdata[power_type]) else 0
                for power_type in powerdata_datatype
            }
            data["Date"] = powerdata['Demand'][i].date.strftime("%Y/%m/%d")
            # add power generation field for response
            data["Generate"] = round(
                data["WT"] + data["PV"] + data["EV"] + data["ESS"], 3
            )
            # add power consumption field for response
            data["Consume"] = round(data["Demand"] - data["Generate"], 3)
            # append data to powerdata_list
            powerdata_list.append(data)
        return make_response(jsonify(powerdata_list))

    # pylint: enable=R0201

    # pylint: disable=R0201
    def summary_mode(self, start_time, end_time, field):
        # referencing the powerdata_datatype object
        powerdata_datatype = self.powerdata_datatype
        # gather date summary by traversing the power_datatype objects
        data = {}
        for data_type in powerdata_datatype:
            # the kW record per minute should divide by 60 to convert to kWh
            powerdata_sum = (
                db.session.query((func.sum(powerdata_datatype[data_type]['field']) / 60).label('sum'))
                .filter(
                    powerdata_datatype[data_type]['model'].updated_at.between(start_time, end_time),
                    powerdata_datatype[data_type]['model'].field == field,
                )
                .first()
                .sum
            )
            data[data_type] = round(powerdata_sum if powerdata_sum else 0, 3)
        # add power generation field for response
        data["Generate"] = round(data["WT"] + data["PV"] + data["EV"] + data["ESS"], 3)
        # add power consumption field for response
        data["Consume"] = round(data["Demand"] - data["Generate"], 3)
        return make_response(jsonify(data))

    # pylint: enable=R0201
