from flask import jsonify
from flask_restful import Resource
from loguru import logger

from utils.socketio import socketio
from scripts.test_settlement import get_settlement


class SocketResource(Resource):
    # pylint: disable=R0201
    def post(self):
        socketio.emit("transaction", get_settlement())
        logger.info("[Emit Settlement Transactions]\nMessage sent")
        return jsonify({"msg": "Successfulling emitted settlement transactions"})

    # pylint: enable=R0201
