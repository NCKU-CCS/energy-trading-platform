import base64
import json
from datetime import datetime, date
from Cryptodome.Hash import SHA256

from config import PLAT_CIPHER, PLAT_SIGNER, RANDOM_GENERATOR, TAG_TEMPLATE
from utils.utils import get_tx_hash, get_data
from endpoints.address.model import AMI, History
from endpoints.powerdata.model import PowerData, Demand, ESS, EV, PV, WT


# Convert IOTA's tag to relate database model.
# tag format: {BEMS}9{IOTA data type}9
# In IOTA, tag must be A-Z and 9, so using '9' to replace Space.
IOTA_DATA_TYPE = {
    'BEMS9HOMEPAGE9INFORMATION9': Demand,
    'BEMS9ESS9DISPLAY9': ESS,
    'BEMS9EV9DISPLAY9': EV,
    'BEMS9PV9DISPLAY9': PV,
    'BEMS9WT9DISPLAY9': WT,
}


def process_data():
    # get address from db
    addresses = [str(ami.iota_address) for ami in AMI.query.all()]
    # generate tags by time
    tags = [tag + chr(ord('A') + datetime.now().hour) for tag in TAG_TEMPLATE]
    for address in addresses:
        for tag in tags:
            # addresses -> Transaction Hash
            transaction_hash = get_tx_hash(addresses=[address], tags=[tag])
            if not transaction_hash:
                continue
            # filt transaction hash by db
            db_hash = [data.address for data in PowerData.query.all()]
            transactions = [tx for tx in transaction_hash if tx not in db_hash]
            # Tx Hash -> message
            if not transactions:
                continue
            messages = get_data(transactions)
            for receive_address in messages:
                # decrypt
                decrypt_data = PLAT_CIPHER.decrypt(
                    base64.b64decode(messages[receive_address]['data']), RANDOM_GENERATOR
                )
                # signature
                # pylint: disable=E1102
                is_verify = PLAT_SIGNER.verify(
                    SHA256.new(decrypt_data), base64.b64decode(messages[receive_address]['signature'])
                )
                # pylint: enable=E1102
                if is_verify:
                    print(decrypt_data)
                    # insert into db
                    try:
                        IOTA_DATA_TYPE[tag[:-1]].add(
                            IOTA_DATA_TYPE[tag[:-1]](
                                json.loads(decrypt_data.decode()),
                                History.query.filter_by(iota_address=address, time=date.today()).first().uuid,
                                str(receive_address),
                            )
                        )
                    except KeyError:
                        pass


process_data()
