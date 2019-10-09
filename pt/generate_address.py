import iota
from config import APP as app

API = iota.Iota(app.config['API_URI'][0], app.config['SEED'])


def get_addresses(index, count):
    return API.get_new_addresses(index=index, count=count)['addresses']
