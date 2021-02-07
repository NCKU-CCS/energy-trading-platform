from flask import g, jsonify
from flask_httpauth import HTTPTokenAuth
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadSignature
from loguru import logger

from endpoints.user.model import User

from config import APP_SECRET_KEY

# pylint: disable=C0103
# one day for 86400 seconds
serializer = Serializer(APP_SECRET_KEY, expires_in=86400)
# pylint: enable=C0103

# pylint: disable=C0103
auth = HTTPTokenAuth(scheme='Bearer')
# pylint: enable=C0103


@auth.verify_token
def verify_token(token):
    try:
        long_lived_token = serializer.loads(token.encode('utf-8'))
    except BadSignature:
        g.error_message = 'Unauthorized access'
        logger.error(f"Login Faild: BadSignature\ntoken: {token}")
        return False

    # get username and uuid from database
    user = User.query.filter_by(tag=long_lived_token).first()
    if user:
        g.uuid = user.uuid
        g.account = user.account
        g.role = user.role
        logger.success(f"Login Success: {user.account}")
        return True
    logger.error("Login Faild: Invalid User")
    g.error_message = 'Access denied'
    return False


@auth.error_handler
def unauthorized():
    return jsonify({'error': g.error_message}), 401
