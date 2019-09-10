from flask_restful import Resource

class Get_address (Resource):
    # token check
    def post(self, tx_hash):
        # Generate address
        return {
            'message': "OK"
        }, 200
