import base64
import json
import sys

from datetime import datetime, date
from sqlalchemy import extract
from Cryptodome.Hash import SHA256
from loguru import logger

sys.path.insert(0, "../energy-trading-platform/pt")

# pylint: disable=C0413
from config import (
    PLAT_CIPHER,
    PLAT_SIGNER,
    RANDOM_GENERATOR,
    TAG_TEMPLATE,
)  # noqa: E402
from utils.utils import get_tx_hash, get_data  # noqa: E402
from endpoints.address.model import AMI, History  # noqa: E402
from endpoints.powerdata.model import PowerData, Demand, ESS, EV, PV, WT  # noqa: E402

# pylint: enable=C0413


def process_data():
    # Convert IOTA's tag to relate database model.
    # tag format: {BEMS}9{IOTA data type}9
    # In IOTA, tag must be A-Z and 9, so using '9' to replace Space.
    iota_data_type = {
        "BEMS9HOMEPAGE9INFORMATION9": Demand,
        "BEMS9ESS9DISPLAY9": ESS,
        "BEMS9EV9DISPLAY9": EV,
        "BEMS9PV9DISPLAY9": PV,
        "BEMS9WT9DISPLAY9": WT,
    }
    # get address from db
    addresses = [str(ami.iota_address) for ami in AMI.query.all()]
    # generate tags by time
    tags = [tag + chr(ord("A") + datetime.now().hour) for tag in TAG_TEMPLATE]
    for address in addresses:
        for tag in tags:
            # addresses -> Transaction Hash
            transaction_hash = get_tx_hash(addresses=[address], tags=[tag])
            if not transaction_hash:
                continue
            # filt transaction hash by db
            db_hash = [
                data.address
                for data in PowerData.query.filter(
                    extract("year", PowerData.updated_at) == date.today().year,
                    extract("month", PowerData.updated_at) == date.today().month,
                    extract("day", PowerData.updated_at) == date.today().day,
                ).all()
            ]
            transactions = [tx for tx in transaction_hash if tx not in db_hash]
            logger.info(f"get {len(transactions)} {tag} data")
            # Tx Hash -> message
            if not transactions:
                continue
            messages = get_data(transactions)
            for receive_address in messages:
                # decrypt
                decrypt_data = PLAT_CIPHER.decrypt(
                    base64.b64decode(messages[receive_address]["data"]),
                    RANDOM_GENERATOR,
                )
                # signature
                # pylint: disable=E1102
                is_verify = PLAT_SIGNER.verify(
                    SHA256.new(decrypt_data),
                    base64.b64decode(messages[receive_address]["signature"]),
                )
                # pylint: enable=E1102
                if is_verify:
                    # insert into db
                    data_type = iota_data_type[tag[:-1]]
                    insert_data = json.loads(decrypt_data.decode())
                    # parse day result from datetime.isoformat
                    # to process the time difference between IOTA and database
                    # python3.7+ can use datetime.fromisoformat(<isoformat>)
                    data_time = insert_data["updated_at"][:10]
                    insert_data["history_id"] = (
                        History.query.filter_by(iota_address=address, time=data_time)
                        .first()
                        .uuid
                    )
                    insert_data["address"] = str(receive_address)

                    # Handling different names
                    insert_data["uuid"] = insert_data.pop("id")
                    if data_type == EV:
                        insert_data["power_display"] = insert_data.pop("power")
                    elif data_type == PV:
                        insert_data["pac"] = insert_data.pop("PAC")
                    elif data_type == WT:
                        insert_data["windgridpower"] = insert_data.pop("WindGridPower")

                    data_type(**insert_data).add()


if __name__ == "__main__":
    process_data()
