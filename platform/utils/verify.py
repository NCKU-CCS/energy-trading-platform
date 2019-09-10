import requests
import json
import hashlib
import base64
from config import app

def verify_data(Tx, data):
    r = requests.get(app.config['API_GETTX']+Tx)
    message = r.json()
    json_data = json.dumps(data).encode('utf-8')
    hash_data = hashlib.sha256(
        json_data).hexdigest().encode()
    base64_data = base64.b64encode(hash_data).decode()
    if base64_data == message['message']['value']:
        return True
    else:
        return False
