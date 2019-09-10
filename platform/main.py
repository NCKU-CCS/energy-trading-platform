from flask import Flask
from flask_restful import Api
from resources.get_address import Get_address
from config import app

api = Api(app)

api.add_resource(Get_address, "/bems/get_address")

if __name__ == "__main__":
    app.run(host=app.config['HOST'], port=app.config['PORT'], debug='no')
