import os
import sys
from datetime import datetime, time, timedelta

from loguru import logger

# pylint: disable=C0413
sys.path.insert(0, os.environ.get("WORK_DIR", "./"))  # WORK_DIR is for development
from endpoints.user.model import User  # noqa: E402

# pylint: enable=C0413


def get_contract_creator():
    creator = User.query.filter_by(contract_creator=True).first()
    if creator:
        logger.info(f"[Get User Request]\nCreator Address:{creator.eth_address}\nEncrypted secret:{creator.eth_secret}")
        return creator.eth_address, creator.eth_secret
    raise LookupError("Sorry, no contractor creator in the database.")


def get_event_time(time_now):
    start_time = time_now + timedelta(hours=1)  # get bid event time
    start_time = datetime.combine(start_time.date(), time(start_time.hour, 0))  # truncate min and sec of event_time
    end_time = start_time + timedelta(hours=1)
    event_time_str = start_time.strftime("%Y-%m-%d %H")  # make time string for contract
    return start_time, end_time, event_time_str


def get_execution_time(time_now):
    return datetime.combine(time_now.date(), time(time_now.hour, 0))
