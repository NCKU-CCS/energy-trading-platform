from datetime import date
from flask import jsonify, request, make_response
from flask_restful import Resource
from utils.logging import logging
from utils.oauth import auth, g
from .model import Data
from ..address.model import AMI, History


class DatasResource(Resource):
    # pylint: disable=R0201
    @auth.login_required
    def get(self):
        if request.args.get('time'):
            time = request.args.get('time')
        else:
            time = date.today()
        logging.info(
            "[Get Datas Request]\nUser Account:%s\nUUID:%s\n" % (g.account, g.uuid)
        )
        datas = []

        # pylint: disable=C0301
        if not History.query.filter_by(time=time, ami_id=AMI.query.filter_by(user_id=g.uuid).first().uuid).first(): # NOQA
            return make_response(jsonify([]))
        # pylint: enable=C0301

        # pylint: disable=C0301
        for message in Data.query.filter_by(history_id=(History.query.filter_by(time=time, ami_id=AMI.query.filter_by(user_id=g.uuid).first().uuid).first().uuid)).all(): # NOQA
            if message.data_type == 'Homepage':
                power = message.grid
            elif message.data_type == 'ESS' or message.data_type == 'EV':
                power = message.power_display
            elif message.data_type == 'PV':
                power = message.PAC
            elif message.data_type == 'WT':
                power = message.WindGridPower
            datas.append(
                {
                    "id": message.uuid,
                    "time": message.updated_at.strftime('%Y/%m/%d %H:%M'),
                    "data_type": message.data_type,
                    "power_display": str(power),
                    "address": 'https://thetangle.org/transaction/' + message.address,
                }
            )
        datas = sorted(datas, key=lambda x: x['time'], reverse=True)
        response = jsonify(datas)
        response.status_code = 200
        return response
        # pylint: enable=C0301

    # pylint: enable=R0201
