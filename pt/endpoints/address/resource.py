from datetime import date
from flask import jsonify
from flask import g as g_ami
from flask_restful import Resource
from flask_httpauth import HTTPTokenAuth
from utils.logging import logging
from utils.oauth import auth, g
from .model import address, AMI

# pylint: disable=C0103
auth_ami = HTTPTokenAuth(scheme='Bearer')
# pylint: enable=C0103
@auth_ami.verify_token
def verify_token(token):
    # get username and uuid from database
    ami = address(token, date.today())
    if ami:
        g_ami.uuid = ami.uuid
        g_ami.name = ami.name
        g_ami.address = ami.iota_address
        return True
    return False


class AddressResource(Resource):
    # pylint: disable=R0201
    @auth_ami.login_required
    def get(self):
        logging.info(
            "[Get Address Request]\nUser name:%s\nUUID:%s\nIOTA Address:%s"
            % (g_ami.name, g_ami.uuid, g_ami.address)
        )
        response = jsonify({"address": g_ami.address})
        response.status_code = 200
        return response
    # pylint: enable=R0201

class AmiResource(Resource):
    # pylint: disable=R0201
    @auth.login_required
    def get(self):
        logging.info(
            "[Get Amis Request]\nUser Account:%s\nUUID:%s"
            % (g.account, g.uuid)
        )
        amis = []
        for ami in AMI.query.filter_by(user_id=g.uuid).all():
            amis.append({
                "id": ami.uuid,
                "name": ami.name,
                "description": ami.description
            })

        response = jsonify(amis)
        response.status_code = 200
        return response
    # pylint: enable=R0201
