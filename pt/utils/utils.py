import json
from typing import List

import iota
from loguru import logger
import requests

from config import API_URI


def get_tx_hash(addresses, tags):
    api = iota.Iota(check_nodes(API_URI)[0])
    transaction_hash = api.find_transactions(addresses=addresses, tags=tags)['hashes']
    return transaction_hash


def get_data(transaction_hash):
    api = iota.Iota(check_nodes(API_URI)[0])
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


def is_confirmed(transaction_hash):
    api = iota.Iota(check_nodes(API_URI)[0])
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
