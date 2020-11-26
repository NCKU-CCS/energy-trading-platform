import json
from datetime import datetime

import iota

from config import API_TRACK as API


def get_tx_hash(addresses, tags):
    transaction_hash = API.find_transactions(addresses=addresses, tags=tags)['hashes']
    return transaction_hash


def get_data(transaction_hash):
    # from transactions get trytes
    trytes = API.get_trytes(hashes=transaction_hash)['trytes']
    # trytes to string(json type)
    messages = {}
    for tx_hash, message in zip(transaction_hash, trytes):
        try:
            transaction = iota.Transaction.from_tryte_string(message)
            messages[tx_hash] = json.loads(
                transaction.signature_message_fragment.decode()
            )
        except json.decoder.JSONDecodeError:
            messages[tx_hash] = 'error'
    return messages


def is_confirmed(transaction_hash):
    confirmed = bool(
        list(API.get_latest_inclusion([transaction_hash])['states'].values())[0]
    )
    return confirmed


def convert_time_zone(time_object: datetime, from_tz, to_tz):
    """Convert DateTime's Time Zone"""
    return (
        time_object.replace(tzinfo=from_tz)
        .astimezone(to_tz)
        .replace(tzinfo=None)
    )
