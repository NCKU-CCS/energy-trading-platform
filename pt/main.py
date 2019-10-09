from flask_restful import Api
from resources.get_address import Get_Address
from config import APP as app

API = Api(app)

API.add_resource(Get_Address, "/bems/get_address")

if __name__ == "__main__":
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug='no',
        ssl_context=app.config['SSL_CONTEXT'],
    )
