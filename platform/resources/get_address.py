from flask import g
from flask_restful import Resource
from flask_httpauth import HTTPTokenAuth
from config import app
from utils.logging import logging

auth = HTTPTokenAuth(scheme='Token')

tokens = app.config['TOKEN']

@auth.verify_token
def verify_token(token):
    if token in tokens:
        g.current_user = tokens[token]
        logging.info("User Login: %s" % g.current_user)
        return True
    return False

class Get_address (Resource):
    # token check
    @auth.login_required
    def post(self, name):
        # Check time
        
        # Check field
        if name not in app.config['ADDRESS']:
            # Generate new address
            pass
        address = app.config['ADDRESS'][name]
        logging.info("[Get_address Request]\nUser:%s\nField:%s\nReturn Address:%s" % (g.current_user, name, address))

        return {
            'address': address
        }, 200
