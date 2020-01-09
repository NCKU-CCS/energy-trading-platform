"""
This file is to generate socketio instance for the app
and define any socket events that will be used.

At this point, only 'connect' event is required.
It does the connection verification which the authentication
implementation is exactly same as the one API verification uses,
but need to implement indivisually.
"""

from flask import request
# pylint: disable=W0622
from flask_socketio import SocketIO, ConnectionRefusedError
# pylint: enable=W0622
from itsdangerous import BadSignature

from utils.oauth import serializer
from utils.logging import logging
from endpoints.user.model import User


# pylint: disable=C0103
socketio = SocketIO()
# pylint: enable=C0103


@socketio.on('connect')
def is_verified():
    verified = False
    # Verify token
    token = request.args.get('token')
    if token is not None:
        try:
            long_lived_token = serializer.loads(token.encode('utf-8'))
            user = User.query.filter_by(tag=long_lived_token).first()
            if user:
                logging.info(
                    "[SocketIO]\nClient connected"
                )
                verified = True
            else:
                logging.info(
                    "[SocketIO]\nLong-lived token does not match any database entry"
                )
        # BadSignature catch nothing
        except BadSignature:
            logging.info(
                "[SocketIO]\nShort-lived token expired or invalid"
            )
    else:
        logging.info(
            "[SocketIO]\nShort-lived token not provided"
        )

    if verified is False:
        raise ConnectionRefusedError("Unauthorized access")
