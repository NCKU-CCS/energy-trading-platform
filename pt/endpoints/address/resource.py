from datetime import date
from flask import g, jsonify
from flask_restful import Resource
from flask_httpauth import HTTPTokenAuth
from utils.logging import logging
from .model import address

# pylint: disable=C0103
auth = HTTPTokenAuth(scheme='Bearer')
# pylint: enable=C0103
@auth.verify_token
def verify_token(token):
    # get username and uuid from database
    ami = address(token, date.today())
    if ami:
        g.uuid = ami.uuid
        g.name = ami.name
        g.address = ami.iota_address
        # print(g.time, date.today())
        return True
    return False


class AddressResource(Resource):
    # pylint: disable=R0201
    @auth.login_required
    def get(self):
        logging.info(
            "[Get Address Request]\nUser name:%s\nUUID:%s\nIOTA Address:%s"
            % (g.name, g.uuid, g.address)
        )
        response = jsonify({"address": g.address})
        response.status_code = 200
        return response

    # pylint: enable=R0201
