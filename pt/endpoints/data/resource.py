from datetime import date
from flask import jsonify, request
from flask_restful import Resource
from utils.logging import logging
from utils.oauth import auth, g
from .model import Data
# UUID -> data(history(ami).today)
from ..user.model import User
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
            "[Get Datas Request]\nUser Account:%s\nUUID:%s\n"
            % (g.account, g.uuid)
        )
        datas = []
        # print(Data.query.filter_by(history_id=(History.query.filter_by(time=time, ami_id=AMI.query.filter_by(user_id=g.uuid).first().uuid).first().uuid)).all())
        # print(AMI.query.filter_by(user_id=g.uuid).first().uuid)
        # print(History.query.filter_by(time=time, ami_id='045eecee-4135-4f4b-bad4-4397d7217d3f').first())

        for message in Data.query.filter_by(history_id=(History.query.filter_by(time=time, ami_id=AMI.query.filter_by(user_id=g.uuid).first().uuid).first().uuid)).all():
            if message.type == 'Homepage':
                power = message.grid
            elif message.type == 'ESS' or message.type == 'EV':
                power = message.power_display
            elif message.type == 'PV':
                power = message.PAC
            elif message.type == 'WT':
                power = message.WindGridPower
            datas.append({
                "id": message.uuid,
                "time": message.updated_at.strftime('%Y/%m/%d %H:%M'),
                "type": message.type,
                "power_display": power
            })
        datas = sorted(datas, key=lambda x: x['time'], reverse=True)
        response = jsonify(datas)
        response.status_code = 200
        return response
    # pylint: enable=R0201
