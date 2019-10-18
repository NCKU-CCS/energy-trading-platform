from flask import jsonify
from flask_restful import Resource
from utils.logging import logging
from utils.oauth import auth, g
from .model import User


class UserResource(Resource):
    # pylint: disable=R0201
    @auth.login_required
    def get(self):
        logging.info(
            "[Get User Request]\nUser Account:%s\nUUID:%s"
            % (g.account, g.uuid)
        )
        user = User.query.filter_by(uuid=g.uuid).first()
        response = jsonify({
            "username": user.username,
            "avatar": user.avatar,
            "balance": user.balance,
            "address": user.address,
            "eth_address": user.eth_address
            })
        response.status_code = 200
        return response
    # pylint: enable=R0201
