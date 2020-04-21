import base64
import json
import sys

from datetime import datetime, timezone, timedelta
from sqlalchemy import extract
import sqlalchemy.exc
from loguru import logger
from Cryptodome.Hash import SHA256

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


# Convert IOTA's tag to relate database model.
# tag format: {BEMS}9{IOTA data type}9
# In IOTA, tag must be A-Z and 9, so using '9' to replace Space.
IOTA_DATA_TYPE = {
    "BEMS9HOMEPAGE9INFORMATION9": Demand,
    "BEMS9ESS9DISPLAY9": ESS,
    "BEMS9EV9DISPLAY9": EV,
    "BEMS9PV9DISPLAY9": PV,
    "BEMS9WT9DISPLAY9": WT,
}
DB_DATA_TYPE = ("Demand", "ESS", "EV", "PV", "WT")


def process_data(utc_now=datetime.utcnow()):
    # get address and transaction hash from db
    addresses = [str(ami.iota_address) for ami in AMI.query.all()]
    # generate tags by utc time
    tags = [tag + chr(ord("A") + utc_now.hour) for tag in TAG_TEMPLATE]
    for address in addresses:
        for tag, db_data_type in zip(tags, DB_DATA_TYPE):
            # addresses -> Transaction Hash
            transaction_hash = get_tx_hash(addresses=[address], tags=[tag])
            if not transaction_hash:
                continue
            # filt transaction hash by db
            db_hash = [
                data.address
                for data in PowerData.query.filter(
                    PowerData.data_type == db_data_type,
                    extract("year", PowerData.updated_at) == utc_now.year,
                    extract("month", PowerData.updated_at) == utc_now.month,
                    extract("day", PowerData.updated_at) == utc_now.day,
                    extract("hour", PowerData.updated_at) == utc_now.hour,
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
                    data_type = IOTA_DATA_TYPE[tag[:-1]]
                    insert_data = json.loads(decrypt_data.decode())
                    # parse day result from datetime.isoformat
                    # to process the time difference between IOTA and database
                    # python3.7+ can use datetime.fromisoformat(<isoformat>)
                    # try-catch is to prevent if `second` is an interger
                    try:
                        insert_data["updated_at"] = datetime.strptime(
                            insert_data["updated_at"], "%Y-%m-%dT%H:%M:%S.%f"
                        )
                    except ValueError:
                        insert_data["updated_at"] = datetime.strptime(
                            insert_data["updated_at"], "%Y-%m-%dT%H:%M:%S"
                        )
                    data_time = insert_data["updated_at"].astimezone(timezone.utc).replace(tzinfo=None).date()
                    history = History.query.filter_by(iota_address=address, time=data_time).first()
                    if history:
                        insert_data["history_id"] = history.uuid
                    else:
                        continue
                    insert_data["address"] = str(receive_address)

                    # Handling different names
                    insert_data["uuid"] = insert_data.pop("id")
                    if data_type == EV:
                        insert_data["power_display"] = insert_data.pop("power")
                    elif data_type == PV:
                        insert_data["pac"] = insert_data.pop("PAC")
                    elif data_type == WT:
                        insert_data["windgridpower"] = insert_data.pop("WindGridPower")
                    try:
                        data_type(**insert_data).add()
                    except sqlalchemy.exc.IntegrityError:
                        logger.error(f"DB Insert Error: Unique Violation\nre-inserted data id: {insert_data['uuid']}")


if __name__ == "__main__":
    process_data(datetime.utcnow() - timedelta(minutes=1))
