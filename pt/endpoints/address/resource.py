from datetime import datetime

from flask import jsonify
from flask import g as g_ami
from flask_restful import Resource
from loguru import logger
from flask_httpauth import HTTPTokenAuth

from utils.oauth import auth, g
from .model import get_address, AMI

# pylint: disable=C0103
auth_ami = HTTPTokenAuth(scheme="Bearer")
# pylint: enable=C0103
@auth_ami.verify_token
def verify_token(token):
    # get username and uuid from database
    ami = get_address(token, datetime.utcnow().date())
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
        logger.info(
            f"[Get Address Request]\nUser name:{g_ami.name}\nUUID:{g_ami.uuid}\nIOTA Address:{g_ami.address}"
        )
        response = jsonify({"address": g_ami.address})
        return response

    # pylint: enable=R0201


class AmiResource(Resource):
    # pylint: disable=R0201
    @auth.login_required
    def get(self):
        logger.info(f"[Get Amis Request]\nUser Account:{g.account}\nUUID:{g.uuid}")
        amis = [
            {"id": ami.uuid, "name": ami.name, "description": ami.description}
            for ami in AMI.query.filter_by(user_id=g.uuid).all()
        ]
        response = jsonify(amis)
        return response

    # pylint: enable=R0201
