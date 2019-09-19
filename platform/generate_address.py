import iota
from config import app

api = iota.Iota(app.config['API_URI'][0], app.config['SEED'])

def get_addresses(index, count):
    return api.get_new_addresses(index=index, count=count)['addresses']
