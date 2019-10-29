from flask import jsonify, make_response
from flask_restful import Resource, reqparse
from werkzeug.security import generate_password_hash, check_password_hash

from utils.logging import logging
from utils.oauth import auth, g
from .model import User


class UserResource(Resource):
    def __init__(self):
        # User Change Password
        self._set_put_parser()

    def _set_put_parser(self):
        self.put_parser = reqparse.RequestParser()
        self.put_parser.add_argument(
            "original_passwd",
            type=str,
            required=True,
            location="json",
            help="Reset password: original_passwd is required",
        )
        self.put_parser.add_argument(
            "new_passwd",
            type=str,
            required=True,
            location="json",
            help="Reset password: new_passwd is required",
        )

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
        args = self.put_parser.parse_args()
        if check_password_hash(user.password, args["original_passwd"]):
            user.password = generate_password_hash(args["new_passwd"])
            User.update(user)
            response = jsonify({"message": "Accept."})
        else:
            response = jsonify({"message": "Reject."})
            response.status_code = 400
        return response

    # pylint: enable=R0201


class LoginResource(Resource):
    def __init__(self):
        # User Login
        self._set_post_parser()

    def _set_post_parser(self):
        self.post_parser = reqparse.RequestParser()
        self.post_parser.add_argument(
            "account",
            type=str,
            required=True,
            location="json",
            help="Post Login: account is required",
        )
        self.post_parser.add_argument(
            "password",
            type=str,
            required=True,
            location="json",
            help="Post Login: password is required",
        )

    # pylint: disable=R0201
    def post(self):
        args = self.post_parser.parse_args()
        user = User.query.filter_by(account=args["account"]).first()
        if user:
            if check_password_hash(user.password, args["password"]):
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
        response = jsonify({"id": g.uuid, "bearer": g.tag})
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
