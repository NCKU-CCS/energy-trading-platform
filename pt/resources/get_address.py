from flask import g
from flask_restful import Resource
from flask_httpauth import HTTPTokenAuth
from utils.logging import logging
from datetime import date
from database import get_address, check_uploader


auth = HTTPTokenAuth(scheme='Bearer')


@auth.verify_token
def verify_token(token):
    user = check_uploader(token)
    if user:
        g.current_user = user
        logging.info("User Login: %s" % g.current_user)
        return True
    return False


class Get_Address(Resource):
    # token check
    @auth.login_required
    def post(self):
        name = str(g.current_user)
        address = get_address(name, date.today())

        logging.info(
            "[Get_Address Request]\nUser name:%s\nField name:%s\nReturn Address:%s"
            % (g.current_user, name, address)
        )

        return {'address': address}, 200
