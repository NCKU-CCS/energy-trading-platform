from flask import g, jsonify
from flask_httpauth import HTTPTokenAuth
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from endpoints.user.model import User

from config import APP_SECRET_KEY

# pylint: disable=C0103
serializer = Serializer(APP_SECRET_KEY, expires_in=600)
# pylint: enable=C0103

# pylint: disable=C0103
auth = HTTPTokenAuth(scheme='Bearer')
# pylint: enable=C0103
@auth.verify_token
def verify_token(token):
    long_lived_token = serializer.loads(token.encode('utf-8'))

    # get username and uuid from database
    user = User.query.filter_by(tag=long_lived_token).first()
    if user:
        g.uuid = user.uuid
        g.account = user.account
        return True
    return False


@auth.error_handler
def unauthorized():
    return jsonify({'error': 'Unauthorized access'}), 401
