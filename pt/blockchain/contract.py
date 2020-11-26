"""
Contract initialization:
1. Get ABI from file.
2. Get contract_creator's secret
3. Establish http connection with Ethereum TestNet (Ropsten) via Infura Node.
4. Setup contract creator and contract instance.

Contract method invocation:
1. Provide a nounce (from web3 docs example).
2. Propose a transaction (return tx_hash).
3. Sign the transaction with creator's authorization.
4. Get transaction hash upon sendTransaction call.
5. Use waitForTransactionReceipt to get receipt detail.
6. Return tx hash.
"""

import json

from web3 import Web3

from utils.utils import SecretCrypto
from config import INFURA_PROJECT_ID, CONTRACT_ADDRESS, ABI_PATH, AES_KEY


# pylint: disable=E1101
class Contract():
    def __init__(self, creator_addr, creator_secret):
        # decriptor for ethereum account secret
        self.cipher = SecretCrypto(AES_KEY)

        # contract abi
        with open(ABI_PATH) as json_file:
            abi = json.load(json_file)

        # project infura node
        infura_url = f'https://ropsten.infura.io/v3/{INFURA_PROJECT_ID}'

        #  establish infura node connection
        self.web3 = Web3(Web3.HTTPProvider(infura_url))

        # setup owner/creator account
        self.creator_addr = creator_addr
        self.private_key = self.cipher.decrypt(creator_secret)

        # setup contract
        self.contract = self.web3.eth.contract(abi=abi, address=CONTRACT_ADDRESS)

    def bid(self, bidder, time, bid_type, volumes, prices):
        nonce = self.web3.eth.getTransactionCount(self.creator_addr)
        tx_hash = self.contract.functions.bid(
            bidder,
            time,
            bid_type,
            volumes,
            prices,
        ).buildTransaction({
            "from": self.creator_addr,
            "nonce": nonce,
            'gas': 5000000,
            'gasPrice': self.web3.toWei('1', 'gwei')
        })
        signed = self.web3.eth.account.signTransaction(tx_hash, self.private_key)
        transaction = self.web3.toHex(self.web3.eth.sendRawTransaction(signed.rawTransaction))
        receipt = self.web3.eth.waitForTransactionReceipt(transaction)
        return self.contract.events.bid_log().processReceipt(receipt)

    def match_bids(self, time, values, prices, buyers, sellers):
        nonce = self.web3.eth.getTransactionCount(self.creator_addr)

        # unpack matchresult
        tx_hash = self.contract.functions.match_bids(
            time,
            values,
            prices,
            buyers,
            sellers,
        ).buildTransaction({
            "from": self.creator_addr,
            "nonce": nonce,
            'gas': 7000000,
            'gasPrice': self.web3.toWei('1', 'gwei')
        })
        signed = self.web3.eth.account.signTransaction(tx_hash, self.private_key)
        transaction = self.web3.toHex(self.web3.eth.sendRawTransaction(signed.rawTransaction))
        receipt = self.web3.eth.waitForTransactionReceipt(transaction)
        return self.contract.events.matched_log().processReceipt(receipt)

    def settlement(self, settlement):
        nonce = self.web3.eth.getTransactionCount(self.creator_addr)

        tx_hash = self.contract.functions.settlement(*settlement).buildTransaction({
            "from": self.creator_addr,
            "nonce": nonce,
            'gas': 7000000,
            'gasPrice': self.web3.toWei('1', 'gwei')
        })
        signed = self.web3.eth.account.signTransaction(tx_hash, self.private_key)
        transaction = self.web3.toHex(self.web3.eth.sendRawTransaction(signed.rawTransaction))
        receipt = self.web3.eth.waitForTransactionReceipt(transaction)
        return self.contract.events.matched_log().processReceipt(receipt)

    def dr_log(self, data_str):

        nonce = self.web3.eth.getTransactionCount(self.creator_addr)

        tx_hash = self.contract.functions.DR_result(data_str).buildTransaction({
            "from": self.creator_addr,
            "nonce": nonce,
            'gas': 7000000,
            'gasPrice': self.web3.toWei('1', 'gwei')
        })
        signed = self.web3.eth.account.signTransaction(tx_hash, self.private_key)
        transaction = self.web3.toHex(self.web3.eth.sendRawTransaction(signed.rawTransaction))
        receipt = self.web3.eth.waitForTransactionReceipt(transaction)
        return self.contract.events.dr_log().processReceipt(receipt)

# pylint: enable=E1101
