from flask import jsonify, request, make_response
from flask_restful import Resource
from werkzeug.security import generate_password_hash, check_password_hash

from utils.logging import logging
from utils.oauth import auth, g, serializer
from .model import User


class UserResource(Resource):
    # pylint: disable=R0201
    @auth.login_required
    def get(self):
        logging.info(
            "[Get User Request]\nUser Account:%s\nUUID:%s" % (g.account, g.uuid)
        )
        user = User.query.filter_by(uuid=g.uuid).first()
        response = jsonify(
            {
                "username": user.username,
                "avatar": user.avatar,
                "balance": user.balance,
                "address": user.address,
                "eth_address": user.eth_address,
            }
        )
        return response

    # pylint: enable=R0201

    # pylint: disable=R0201
    @auth.login_required
    def put(self):
        logging.info(
            "[Put User Request]\nUser Account:%s\nUUID:%s" % (g.account, g.uuid)
        )
        user = User.query.filter_by(uuid=g.uuid).first()
        data = request.get_json()
        if check_password_hash(user.password, data["original_passwd"]):
            user.password = generate_password_hash(data["new_passwd"])
            User.update(user)
            response = jsonify({"message": "Accept."})
        else:
            response = jsonify({"message": "Reject."})
            response.status_code = 400
        return response

    # pylint: enable=R0201


class LoginResource(Resource):
    # pylint: disable=R0201
    def post(self):
        data = request.get_json()
        user = User.query.filter_by(account=data["account"]).first()
        if user:
            if check_password_hash(user.password, data["password"]):
                g.username = user.username
                g.uuid = user.uuid
                g.tag = user.tag
            else:
                return make_response(jsonify({"error": "Unauthorized access"}), 401)
        else:
            return make_response(jsonify({"error": "Unauthorized access"}), 401)
        logging.info(
            "[Post Login Request]\nUser Account:%s\nUUID:%s" % (g.username, g.uuid)
        )
        short_lived_token = serializer.dumps(g.tag).decode('utf-8')
        print(short_lived_token)
        response = jsonify({"id": g.uuid, "bearer": short_lived_token})
        return response

    # pylint: enable=R0201


class ParticipantResource(Resource):
    # pylint: disable=R0201
    @auth.login_required
    def get(self):
        logging.info(
            "[Get Participant Request]\nUser Account:%s\nUUID:%s" % (g.account, g.uuid)
        )
        bems = [{"id": user.uuid, "name": user.username} for user in User.query.all()]
        response = jsonify(bems)
        return response

    # pylint: enable=R0201
