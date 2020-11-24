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
from config import PLAT_CIPHER, PLAT_SIGNER, RANDOM_GENERATOR, TAG_TEMPLATE, API_URI, API_OPEN  # noqa: E402
from utils.utils import get_tx_hash, get_data, check_nodes  # noqa: E402
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
    """get data from db

    Arguments:
        utc_now {datetime} -- set time to query
        db_data_type {string} -- set data_type to query

    Returns:
        db_uuid {tuple} -- uuids in db
        db_address {tuple} -- addresses in db
    """
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
    """decrypt data with base64 and RSA

    Arguments:
        receive_data {dict} -- include data and signature

    Returns:
        decrypt_data {string} -- raw data
        is_verify {bool} -- signature verify success or fail
    """
    # decrypt data
    decrypt_data = PLAT_CIPHER.decrypt(base64.b64decode(receive_data["data"]), RANDOM_GENERATOR)

    # check signature
    # pylint: disable=E1102
    is_verify = PLAT_SIGNER.verify(SHA256.new(decrypt_data), base64.b64decode(receive_data["signature"]))
    # pylint: enable=E1102

    return decrypt_data, is_verify


def add_fields(insert_data, address, receive_address):
    """Add fields to data

    Arguments:
        insert_data {dict} -- data
        address {string} -- iota receiver address
        receive_address {string} -- iota transaction address
    """
    # parse day result from datetime.isoformat
    # to process the time difference between IOTA and database
    # python3.7+ can use datetime.fromisoformat(<isoformat>)
    # try-catch is to prevent if `second` is an interger
    try:
        insert_data["updated_at"] = datetime.strptime(insert_data["updated_at"], "%Y-%m-%dT%H:%M:%S.%f")
    except ValueError:
        insert_data["updated_at"] = datetime.strptime(insert_data["updated_at"], "%Y-%m-%dT%H:%M:%S")

    # get upload data's data_time
    data_time = insert_data["updated_at"].astimezone(timezone.utc).replace(tzinfo=None).date()

    # get related history id
    history = History.query.filter_by(iota_address=address, time=data_time).first()
    if history:
        insert_data["history_id"] = history.uuid
    else:
        return False

    # put IOTA address into data_structure
    insert_data["address"] = str(receive_address)
    return True


def uniform_fields(insert_data, db_data_type):
    """Adjust data field name

    Arguments:
        insert_data {dict} -- data
        db_data_type {string} -- insert model name

    """
    insert_data["uuid"] = insert_data.pop("id")
    if db_data_type == "EV":
        insert_data["power_display"] = insert_data.pop("power")
    elif db_data_type == "PV":
        insert_data["pac"] = insert_data.pop("pac")
    elif db_data_type == "WT":
        insert_data["windgridpower"] = insert_data.pop("wind_grid_power")


def insert_to_db(tag, insert_data):
    """Insert data to db

    Arguments:
        tag {string} -- identify insert table
        insert_data {dict} -- data
    """
    data_type = IOTA_DATA_TYPE[tag[:-1]]

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


# pylint: disable=R0914


def main(utc_now=datetime.utcnow()):
    # get address and transaction hash from db
    addresses = (str(ami.iota_address) for ami in AMI.query.all())

    # generate tags by utc time
    tags = [tag + chr(ord("A") + utc_now.hour) for tag in TAG_TEMPLATE]

    # get available IOTA nodes
    available_nodes = check_nodes(API_URI)
    if available_nodes:
        uri = available_nodes[0]
    else:
        uri = API_OPEN
    logger.info(f"[IOTA] URI: {uri}")

    for address in addresses:
        for tag, db_data_type in zip(tags, DB_DATA_TYPE):
            # addresses -> Transaction Hash
            transaction_hash = get_tx_hash(api_uri=uri, addresses=[address], tags=[tag])
            if not transaction_hash:
                continue

            # filt transaction db and hash by db
            db_uuid, db_hash = get_inserted_data(utc_now, db_data_type)
            transactions = [tx for tx in transaction_hash if tx not in db_hash]
            logger.info(f"get {len(transactions)} {tag} data")
            if not transactions:
                continue

            # Tx Hash -> message
            messages = get_data(uri, transactions)

            for receive_address in messages:
                # decrypt data and signature
                decrypt_data, is_verify = get_decrypt_data_sign(messages[receive_address])

                # check signature
                if not is_verify:
                    logger.error(f"Verify Faild\n{decrypt_data}")
                    continue

                # prepare to insert into db
                insert_data = json.loads(decrypt_data.decode())

                # Prevent reinsertion of data using the same uuid
                if insert_data["id"] in db_uuid:
                    logger.error(
                        f"Repeated Insert Error\n\
                        uuid: {insert_data['id']}\n\
                        address: {receive_address}"
                    )
                    continue

                # Add fields with data
                if not add_fields(insert_data, address, receive_address):
                    break

                # Handling different names
                uniform_fields(insert_data, db_data_type)

                # Insert to db
                insert_to_db(tag, insert_data)


# pylint: enable=R0914


if __name__ == "__main__":
    # One minute deduction is to receive the last data of the last hour
    main(datetime.utcnow() - timedelta(minutes=1))
