from datetime import datetime, timedelta
from itertools import tee
from typing import List, Dict
from uuid import uuid4
import json
from csv import DictReader
import requests
from loguru import logger
import pytz

from pt.simulate.config import RAW_DATA_TEMPLATE, UPLOADER_URL, HOST, UPLOAD_TZ


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
    now = convert_time_zone(datetime.now(), pytz.utc, UPLOAD_TZ)
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
    logger.info(f"Payload: {payload}")
    return payload


def send(demand: dict, bems: str):
    now = convert_time_zone(datetime.now(), pytz.utc, UPLOAD_TZ)
    now = now.replace(minute=demand["inserted_at"].minute)
    logger.debug(f"Send Time: {now}")

    payload = form_payload(demand, bems, now)
    
    headers = {"Content-Type": "application/json"}
    res = requests.post(UPLOADER_URL, headers=headers, data=json.dumps(payload))
    logger.info(f"Response Code: {res.status_code}, Response Body: {res.json()}")

def auth(account: str, password: str):
    logger.debug(f"Account: {account}")
    res = requests.post(f"{HOST}/login", json={"account":f"{account}", "password":"test"})
    if(res.status_code == 200):
        return res.json()['bearer']
    else:
        logger.warning("Authorization Failed!")
        return ""


def bidsubmit(token: str, start_time:str, end_time:str, bid_type: str, value: float, price: float):
    logger.debug(f"Bidsubmit Arguments:{locals()}")
    req_body = locals()
    req_body.pop("token")
    res = requests.post(
        f"{HOST}/bidsubmit",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json=req_body
    )
    logger.info(f"Start_Time: {start_time} End_Time: {end_time} Result: {res.json()}")

def convert_time_zone(time_object: datetime, from_tz, to_tz):
    """Convert DateTime's Time Zone"""
    return time_object.replace(tzinfo=from_tz).astimezone(to_tz).replace(tzinfo=None)

def daterange_hours(start_time, end_time):
    for n in range(int((end_time - start_time).total_seconds()//3600)):
        yield start_time + timedelta(hours=n)

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)
