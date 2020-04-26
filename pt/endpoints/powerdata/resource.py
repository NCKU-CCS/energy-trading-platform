from datetime import datetime, timedelta

from flask import jsonify, make_response
from flask_restful import Resource, reqparse
from loguru import logger

from sqlalchemy import cast, func, DATE
from sqlalchemy.dialects.postgresql import INTERVAL
from sqlalchemy.sql.functions import concat
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
            "chart_date",
            type=str,
            required=False,
            location="args",
            help="Get PowerData: chart date is required",
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
        if g.is_aggregator and args["participant_id"]:
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
        if args["chart_date"]:
            logger.info("[Get PowerData Request]:Data Charts Mode")
            chart_date = datetime.strptime(args["chart_date"], "%Y/%m/%d")
            start_time = chart_date - timedelta(days=6)
            end_time = chart_date + timedelta(days=1)
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
        data_list = []
        # The kW record per minute should divide by 60 to convert to kWh
        # Demand 7 days power usage
        demand_list = db.session.query(
            cast(Demand.updated_at + func.cast(concat(8, ' HOURS'), INTERVAL), DATE).label('date'),
            (func.sum(Demand.grid) / 60).label('sum')
        ).filter(
            Demand.uuid.in_(
                [data.uuid for data in PowerData.query.filter(
                    PowerData.updated_at.between(start_time, end_time),
                    PowerData.field == field,
                    PowerData.data_type == 'Demand'
                ).all()]
            )
        ).group_by('date').order_by('date').all()
        # PV 7 days power usage
        pv_list = db.session.query(
            cast(PV.updated_at + func.cast(concat(8, ' HOURS'), INTERVAL), DATE).label('date'),
            (func.sum(PV.pac) / 60).label('sum')
        ).filter(
            PV.uuid.in_(
                [data.uuid for data in PowerData.query.filter(
                    PowerData.updated_at.between(start_time, end_time),
                    PowerData.field == field,
                    PowerData.data_type == 'PV'
                ).all()]
            )
        ).group_by('date').order_by('date').all()
        # EV 7 days power usage
        ev_list = db.session.query(
            cast(EV.updated_at + func.cast(concat(8, ' HOURS'), INTERVAL), DATE).label('date'),
            (func.sum(EV.power_display) / 60).label('sum')
        ).filter(
            EV.uuid.in_(
                [data.uuid for data in PowerData.query.filter(
                    PowerData.updated_at.between(start_time, end_time),
                    PowerData.field == field,
                    PowerData.data_type == 'EV'
                ).all()]
            )
        ).group_by('date').order_by('date').all()
        # ESS 7 days power usage
        ess_list = db.session.query(
            cast(ESS.updated_at + func.cast(concat(8, ' HOURS'), INTERVAL), DATE).label('date'),
            (func.sum(ESS.power_display) / 60).label('sum')
        ).filter(
            ESS.uuid.in_(
                [data.uuid for data in PowerData.query.filter(
                    PowerData.updated_at.between(start_time, end_time),
                    PowerData.field == field,
                    PowerData.data_type == 'ESS'
                ).all()]
            )
        ).group_by('date').order_by('date').all()
        # WT 7 days power usage
        wt_list = db.session.query(
            cast(WT.updated_at + func.cast(concat(8, ' HOURS'), INTERVAL), DATE).label('date'),
            (func.sum(WT.windgridpower) / 60).label('sum')
        ).filter(
            WT.uuid.in_(
                [data.uuid for data in PowerData.query.filter(
                    PowerData.updated_at.between(start_time, end_time),
                    PowerData.field == field,
                    PowerData.data_type == 'WT'
                ).all()]
            )
        ).group_by('date').order_by('date').all()
        # combine each power usage lists into one list
        for i in range(7):
            data = {
                'Date': demand_list[i].date.strftime('%Y-%m-%d'),
                'Demand': round(demand_list[i].sum, 3),
                'PV': round(pv_list[i].sum, 3),
                'EV': round(ev_list[i].sum, 3),
                'ESS': round(ess_list[i].sum, 3),
                'WT': round(wt_list[i].sum, 3)
            }
            # add a calculated field called Generate
            data["Generate"] = round(data['WT'] + data['PV'] + data['EV'] + data['ESS'], 3)
            # add a calculated field called Comsume
            data["Consume"] = round(data['Demand'] - data["Generate"], 3)
            # append each data to final list
            data_list.append(data)
        return make_response(jsonify(data_list))

    # pylint: enable=R0201

    # pylint: disable=R0201
    def summary_mode(self, start_time, end_time, field):
        # The kW record per minute should divide by 60 to convert to kWh
        # Demand sum
        demand_data = db.session.query((func.sum(Demand.grid) / 60).label('sum')).filter(
            Demand.uuid.in_(
                [data.uuid for data in PowerData.query.filter(
                    PowerData.updated_at.between(start_time, end_time),
                    PowerData.field == field,
                    PowerData.data_type == 'Demand'
                ).all()]
            )
        ).all()
        # PV sum
        pv_data = db.session.query((func.sum(PV.pac) / 60).label('sum')).filter(
            PV.uuid.in_(
                [data.uuid for data in PowerData.query.filter(
                    PowerData.updated_at.between(start_time, end_time),
                    PowerData.field == field,
                    PowerData.data_type == 'PV'
                ).all()]
            )
        ).all()
        # EV sum
        ev_data = db.session.query((func.sum(EV.power_display) / 60).label('sum')).filter(
            EV.uuid.in_(
                [data.uuid for data in PowerData.query.filter(
                    PowerData.updated_at.between(start_time, end_time),
                    PowerData.field == field,
                    PowerData.data_type == 'EV'
                ).all()]
            )
        ).all()
        # ESS sum
        ess_data = db.session.query((func.sum(ESS.power_display) / 60).label('sum')).filter(
            ESS.uuid.in_(
                [data.uuid for data in PowerData.query.filter(
                    PowerData.updated_at.between(start_time, end_time),
                    PowerData.field == field,
                    PowerData.data_type == 'ESS'
                ).all()]
            )
        ).all()
        # WT sum
        wt_data = db.session.query((func.sum(WT.windgridpower) / 60).label('sum')).filter(
            WT.uuid.in_(
                [data.uuid for data in PowerData.query.filter(
                    PowerData.updated_at.between(start_time, end_time),
                    PowerData.field == field,
                    PowerData.data_type == 'WT'
                ).all()]
            )
        ).all()
        # record sum to data object
        data = {
            "Demand": round(demand_data[0].sum, 3),
            "WT": round(wt_data[0].sum, 3),
            "PV": round(pv_data[0].sum, 3),
            "EV": round(ev_data[0].sum, 3),
            "ESS": round(ess_data[0].sum, 3)
        }
        # Add Power generation field
        data["Generate"] = round(data['WT'] + data['PV'] + data['EV'] + data['ESS'], 3)
        # Add Power comsumption field
        data["Consume"] = round(data['Demand'] - data["Generate"], 3)
        return make_response(jsonify(data))

    # pylint: enable=R0201
