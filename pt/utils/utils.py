import json
from binascii import b2a_hex, a2b_hex
from datetime import datetime
from typing import List

import iota
import requests
from loguru import logger
from Cryptodome.Cipher import AES


def get_tx_hash(api_uri, addresses, tags):
    api = iota.Iota(api_uri)
    transaction_hash = api.find_transactions(addresses=addresses, tags=tags)['hashes']
    return transaction_hash


def get_data(api_uri, transaction_hash):
    api = iota.Iota(api_uri)
    # from transactions get trytes
    trytes = api.get_trytes(hashes=transaction_hash)['trytes']
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


def is_confirmed(api_uri, transaction_hash):
    api = iota.Iota(api_uri)
    confirmed = bool(
        list(api.get_latest_inclusion([transaction_hash])['states'].values())[0]
    )
    return confirmed


def check_nodes(nodes: List[str], timeout: int = 5) -> List[str]:
    """check available nodes

    Args:
        nodes (List[str]): nodes for testing
        timeout (int): timeout for testing

    Returns:
        List[str]: available nodes
    """
    available_nodes: List[str] = list()
    for node in nodes:
        logger.info(f"[CHECK NODES] Testing {node}")
        try:
            api = iota.Iota(iota.HttpAdapter(node, timeout=timeout))
            # Check node alive
            node_info = api.get_node_info()
            # Show Node Info
            logger.debug(node_info)
            # Check node milestone is latest
            assert node_info["latestMilestone"] == node_info["latestSolidSubtangleMilestone"]
            logger.success(f"[CHECK NODES] Node is alive. URI: {node}")
            available_nodes.append(node)
        except AssertionError:
            logger.warning(f"[CHECK NODES] Node is not up to date. URI: {node}")
        except requests.exceptions.ConnectionError:
            logger.error(f"[CHECK NODES] Node is down. URI: {node}")
        except requests.exceptions.ReadTimeout:
            logger.error(f"[CHECK NODES] Node timeout. URI: {node}")
    return available_nodes


def convert_time_zone(time_object: datetime, from_tz, to_tz):
    """Convert DateTime's Time Zone"""
    return (
        time_object.replace(tzinfo=from_tz)
        .astimezone(to_tz)
        .replace(tzinfo=None)
    )


class SecretCrypto():
    def __init__(self, key):
        self.key = key
        self.mode = AES.MODE_CBC

    def encrypt(self, text):
        cipher = AES.new(self.key, self.mode, self.key)

        # encrypt text must be multiple of 16
        length = 16
        if len(text) % length != 0:
            padding_size = length - (len(text) % length)
        else:
            padding_size = 0

        # add padding null charactor
        text += '\0' * padding_size

        ciphertext = cipher.encrypt(bytes(text, encoding="utf-8"))
        return b2a_hex(ciphertext)

    def decrypt(self, text):
        cipher = AES.new(self.key, self.mode, self.key)
        plain_text = cipher.decrypt(a2b_hex(text))

        # return plain_text with extra null charactors removed
        return plain_text.decode("utf-8").rstrip('\0')
