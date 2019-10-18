from flask import Flask, jsonify
from flask_restful import Api
from werkzeug.exceptions import HTTPException
from werkzeug.exceptions import default_exceptions
from dotenv import load_dotenv

from config import db
from endpoints import RESOURCES


load_dotenv()


# from config import APP as app
# API = Api(app)
# API.add_resource(Get_Address, "/bems/get_address")


def create_app(config_mode):

    app = Flask(__name__)

    @app.errorhandler(Exception)
    def handle_error(error):

        code = 500

        if isinstance(error, HTTPException):
            code = error.code

        # pylint: disable=E1101
        app.logger.warning(f'{code} - {error}')
        # pylint: enable=E1101

        return jsonify(error=str(error)), code

    for ex in default_exceptions:
        app.register_error_handler(ex, handle_error)

    # flask config
    app.config.from_pyfile('./config/config.py')
    # pylint: disable=E1101
    app.logger.info(f'APP Mode: {config_mode}')
    # pylint: enable=E1101

    # DB Init
    db.init_app(app)
    # Route Init
    api = Api(app)
    api.add_resource(RESOURCES['user'], '/user')
    api.add_resource(RESOURCES['address'], '/address')
    api.add_resource(RESOURCES['amis'], '/amis')
    api.add_resource(RESOURCES['news'], '/news')
    api.add_resource(RESOURCES['datas'], '/datas')

    # api.add_resource(RESOURCES['version'], '/version', endpoint='/version')
    # api.add_resource(RESOURCES['echonet'], '/echonet')
    # api.add_resource(RESOURCES['smart_lock'], '/smart_lock')
    return app


def main():
    app = create_app('Develop')
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug='no',
        ssl_context=app.config['SSL_CONTEXT'],
    )


if __name__ == "__main__":
    main()
