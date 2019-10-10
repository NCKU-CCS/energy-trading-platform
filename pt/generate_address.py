from config import API


def get_addresses(index, count):
    return API.get_new_addresses(index=index, count=count)['addresses']
