from datetime import datetime
from csv import DictReader
from typing import List, Dict
from uuid import uuid4
import json
import requests
from loguru import logger

from pt.simulate.config import RAW_DATA_TEMPLATE, UPLOADER_URL


def read(path: str):
    with open(path, "r") as rfile:
        contents = list(DictReader(rfile))
        logger.debug(f"Contents: {contents} Type: {type(contents)}")
    return contents


def carlab_parser(contents: List[Dict]):
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

def abri_parser(contents: List[Dict]):
    """
    Example: [
        OrderedDict([('AMI_1', '11.5'), ('AMI_2', '13.44'), ('AMI_3', '2'), ('', ''), ('total_load(kW)', '26.94'), ('PV_generate(kW)', '0'), ('net_load(kW)', '26.94'), ('TIME', '2020/5/8 20:15')]),
        OrderedDict([('AMI_1', '11.5'), ('AMI_2', '12.16'), ('AMI_3', '2.4'), ('', ''), ('total_load(kW)', '26.06'), ('PV_generate(kW)', '0'), ('net_load(kW)', '26.06'), ('TIME', '2020/5/8 20:30')])
    ]
    """
    processed = sorted(
        [
            {
                "inserted_at": datetime.strptime(line["TIME"], "%Y/%m/%d %H:%M"),
                "grid_power": float(line["total_load(kW)"]),
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
    logger.debug(f"Filtered Result: {filtered_list}")
    return get_nearest(filtered_list, now)


def same_period(target: datetime, compare: datetime):
    if target.weekday() != compare.weekday():
        return False
    if target.hour != compare.hour:
        return False
    return True


def get_nearest(filtered_list: List[dict], target: datetime):
    result = filtered_list[0]
    for sim_data in filtered_list:
        new = abs(target.minute - sim_data["inserted_at"].minute)
        old = abs(target.minute - result["inserted_at"].minute)
        if new < old:
            result = sim_data
    logger.info(f'Filtered Result: {result["inserted_at"]}')
    return result

def form_payload(demand: dict, field: str, time: datetime):
    payload = RAW_DATA_TEMPLATE.copy()
    payload["bems_homepage_information"]["id"] = str(uuid4())
    payload["bems_homepage_information"]["field"] = field
    payload["bems_homepage_information"]["grid"] = demand["grid_power"]
    payload["bems_homepage_information"]["updated_at"] = time.isoformat()
    payload = {f"{field}": payload}
    logger.debug(f"Payload: {payload}")
    return payload


def send(demand: dict, bems: str):
    now = datetime.now()
    now = now.replace(minute=demand["inserted_at"].minute)
    logger.debug(f"Send Time: {now}")

    payload = form_payload(demand, bems, now)
    
    headers = {"Content-Type": "application/json"}
    res = requests.post(UPLOADER_URL, headers=headers, data=json.dumps(payload))
    logger.info(f"Response Code: {res.status_code}, Response Body: {res.json()}")
