import os
import random
import json
from itertools import groupby
from datetime import datetime, timedelta

from sqlalchemy import func, cast, Float

from config import db
from endpoints.bid.model import BidSubmit, Tenders
from endpoints.user.model import User


def get():
    last_three_day = datetime.combine((datetime.now() - timedelta(days=3)).date(), datetime.min.time())
    
    query_bids = BidSubmit.query.filter(BidSubmit.status != "NULL").order_by(BidSubmit.start_time.desc()).all()
    tender_hour_bids = [
        list(grouped_entry)
        for (tender_id, start_time), grouped_entry in groupby(query_bids, lambda bid: (bid.tenders_id, bid.start_time))
    ]
    
    result = [
        {
            "id": bids[0].uuid,
            "date": bids[0].start_time.strftime("%Y/%m/%d"),
            "time": f'{bids[0].start_time.strftime("%H")}:00-{bids[0].end_time.strftime("%H")}:00',
            "bid_type": bids[0].bid_type,
            "win": bids[0].win,
            "status": bids[0].status,
            "transaction_hash": bids[0].transaction_hash,
            "upload": bids[0].upload_time.strftime("%Y/%m/%d %H:%M:%S"),
            "user": {
                "name": bids[0].tenders.user.username,
                "address": bids[0].tenders.user.address,
            },
            "counterpart": {
                "name": bids[0].counterpart_name,
                "address": bids[0].counterpart_address,
            },
            "bids": {
                "price": bids[0].price,
                "value": bids[0].value,
            },
            "wins": {
                "price": bids[0].price,
                "value": bids[0].value,
            },
            "achievement": random.random(),
            "settlement": random.randint(0, 100),
        }
        for bids in tender_hour_bids
    ]
    print(json.dumps(result[0]))

get()