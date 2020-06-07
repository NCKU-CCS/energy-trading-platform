from csv import DictReader
from typing import List, Dict
from loguru import logger
from datetime import datetime
from uuid import uuid4
import requests
import json

from pt.simulate.config import SIMULATE_FILE_PATH

raw_data_template = {
    "bems_homepage_information": {
        "id": "",
        "field": "",
        "grid": 0,
        "pv": 0,
        "building": 0,
        "ess": 0,
        "ev": 0,
        "updated_at": "",
    }
}


def read(path: str):
    with open(path, "r") as rf:
        contents = list(DictReader(rf))
        logger.debug(f"Contents: {contents} Type: {type(contents)}")
    return contents


def parse(contents: List[Dict]):
    """
    Example: [
        OrderedDict([('id', '5121'), ('field', 'carlab'), ('grid_power', '11.689'), ('inserted_at', '2020/5/1 23:30')]),
        OrderedDict([('id', '5122'), ('field', 'carlab'), ('grid_power', '11.883'), ('inserted_at', '2020/5/1 23:45')])
    ]
    """
    processed = sorted(
        [
            {
                "inserted_at": datetime.strptime(line["inserted_at"], "%Y/%m/%d %H:%M"),
                "grid_power": float(line["grid_power"]),
            }
            for line in contents
        ],
        key=lambda x: x["inserted_at"],
    )
    logger.debug(processed)
    return processed


def find_one(processed: List[dict]):
    now = datetime.now()
    logger.info(f"Current Time: {now.isoformat()}")
    filtered_list = list(
        filter(lambda x: same_period(x["inserted_at"], now), processed)
    )
    logger.debug(f"Fitered Result: {filtered_list}")
    return get_nearest(filtered_list, now)


def same_period(target: datetime, compare: datetime):
    if target.weekday() != compare.weekday():
        return False
    elif target.hour != compare.hour:
        return False
    return True


def get_nearest(flist: List[dict], target: datetime):
    result = flist[0]
    for t in flist:
        new = abs(target.minute - t["inserted_at"].minute)
        old = abs(target.minute - result["inserted_at"].minute)
        if new < old:
            result = t
    logger.info(f'Fitered Result: {result["inserted_at"]}')
    return result

def send(demand: dict):
    now = datetime.now()
    now = now.replace(minute=demand["inserted_at"].minute)
    logger.debug(f'Send Time: {now}')
    payload = raw_data_template.copy()
    payload["bems_homepage_information"]["id"] = str(uuid4())
    payload["bems_homepage_information"]["field"] = "Carlab_BEMS"
    payload["bems_homepage_information"]["grid"] = demand["grid_power"]
    payload["bems_homepage_information"]["updated_at"] = now.isoformat()
    payload = {
        "Carlab_BEMS" :  payload
    }
    logger.debug(f'Payload: {payload}')
    headers = {
        "Content-Type": "application/json"
    }
    res = requests.post(
        "http://localhost:4000/bems/upload",
        headers=headers,
        data=json.dumps(payload)
    )
    logger.info(f'Response Code: {res.status_code}, Response Body: {res.json()}')


def main():
    contents = read(SIMULATE_FILE_PATH)
    contents = parse(contents)
    result = find_one(contents)
    send(result)


if __name__ == "__main__":
    main()
