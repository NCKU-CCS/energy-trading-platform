import json
import hashlib
import base64
import requests
from config import APP as app


def verify_data(transaction_hash, data):
    message = requests.get(app.config['API_GETTX'] + transaction_hash).json()
    json_data = json.dumps(data).encode('utf-8')
    hash_data = hashlib.sha256(json_data).hexdigest().encode()
    base64_data = base64.b64encode(hash_data).decode()
    return bool(base64_data == message['message']['value'])
