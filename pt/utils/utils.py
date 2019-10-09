import json
import iota

# from config import API_URI

API_URI = 'http://node10.puyuma.org:14265'

API = iota.Iota(API_URI)


def get_data(transaction_hashs):
    data = API.get_trytes(hashes=transaction_hashs)
    messages = []
    for message in data['trytes']:
        try:
            transaction = iota.Transaction.from_tryte_string(message)
            messages.append(json.loads(transaction.signature_message_fragment.decode()))
        except json.decoder.JSONDecodeError:
            messages.append('error')
    return messages


def is_confirmed(transaction_hash):
    confirmed = bool(
        list(API.get_latest_inclusion([transaction_hash])['states'].values())[0]
    )
    return confirmed
