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
# Content of data_field in db
DB_DATA_TYPE = ("Demand", "ESS", "EV", "PV", "WT")


def get_inserted_data(utc_now, db_data_type):
    # Get inserted data of the hour
    db_datas = [
        (data.uuid, data.address)
        for data in PowerData.query.filter(
            PowerData.data_type == db_data_type,
            extract("year", PowerData.updated_at) == utc_now.year,
            extract("month", PowerData.updated_at) == utc_now.month,
            extract("day", PowerData.updated_at) == utc_now.day,
            extract("hour", PowerData.updated_at) == utc_now.hour,
        ).all()
    ]

    if db_datas:
        # Split uuid and address into two tuples
        return map(tuple, zip(*db_datas))

    # First query of the hour, no inserted data is normal
    return [], []


def get_decrypt_data_sign(receive_data):
    # decrypt data
    decrypt_data = PLAT_CIPHER.decrypt(
        base64.b64decode(receive_data["data"]), RANDOM_GENERATOR
    )

    # check signature
    # pylint: disable=E1102
    is_verify = PLAT_SIGNER.verify(
        SHA256.new(decrypt_data), base64.b64decode(receive_data["signature"])
    )
    # pylint: enable=E1102

    return decrypt_data, is_verify


def uniform_fields(insert_data, data_type):
    insert_data["uuid"] = insert_data.pop("id")
    if data_type == EV:
        insert_data["power_display"] = insert_data.pop("power")
    elif data_type == PV:
        insert_data["pac"] = insert_data.pop("PAC")
    elif data_type == WT:
        insert_data["windgridpower"] = insert_data.pop("WindGridPower")
    return insert_data


def insert_to_db(tag, decrypt_data, db_uuid, address, receive_address):
    data_type = IOTA_DATA_TYPE[tag[:-1]]
    insert_data = json.loads(decrypt_data.decode())

    # Prevent reinsertion of data using the same uuid
    if insert_data["id"] in db_uuid:
        logger.error(
            f"Repeated Insert Error\n\
            uuid: {insert_data['id']}\n\
            address: {insert_data['address']}"
        )
        return

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

    # get upload data's data_time
    data_time = (
        insert_data["updated_at"].astimezone(timezone.utc).replace(tzinfo=None).date()
    )

    # get related history id
    history = History.query.filter_by(iota_address=address, time=data_time).first()
    if history:
        insert_data["history_id"] = history.uuid
    else:
        return

    # put IOTA address into data_structure
    insert_data["address"] = str(receive_address)

    # Handling different names
    insert_data = uniform_fields(insert_data, data_type)

    # Insert data by ORM
    try:
        data_type(**insert_data).add()

    # Check Insert same UUID's data
    except sqlalchemy.exc.IntegrityError:
        logger.error(
            f"DB Insert Error: Unique Violation\n\
            re-inserted data id: {insert_data['uuid']}\n\
            address: {insert_data['address']}"
        )


def main(utc_now=datetime.utcnow()):
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

            # filt transaction db and hash by db
            db_uuid, db_hash = get_inserted_data(utc_now, db_data_type)
            transactions = [tx for tx in transaction_hash if tx not in db_hash]
            logger.info(f"get {len(transactions)} {tag} data")
            if not transactions:
                continue

            # Tx Hash -> message
            messages = get_data(transactions)

            for receive_address in messages:
                # decrypt data and signature
                decrypt_data, is_verify = get_decrypt_data_sign(
                    messages[receive_address]
                )

                # check signature
                if not is_verify:
                    logger.error(f"Verify Faild\n{decrypt_data}")
                    continue

                # insert into db
                insert_to_db(tag, decrypt_data, db_uuid, address, receive_address)


if __name__ == "__main__":
    # One minute deduction is to receive the last data of the last hour
    main(datetime.utcnow() - timedelta(minutes=1))
