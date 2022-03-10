import os
import random
from datetime import datetime, timedelta

from config import db
from endpoints.bid.model import BidSubmit


print("executing")
# this recent 5 hours
action = [None, "未得標", "已結算", "執行中", "已得標", "投標中"]
# action = [None, None, None, None, None]

now = datetime.now()
query_start = datetime(now.year, now.month, now.day, now.hour) - timedelta(hours=3)
query_end = query_start + timedelta(hours=5)

addresses = [
    "金門縣",
    "金門縣金城鎮賢城路1號",
    "金門縣金寧鄉桃園路一號",
    "金門縣金寧鄉大學路1號",
]

names = [
 "金門聚合商",
 "莒光樓",
 "金門酒廠",
 "金門大學",
]

bids = BidSubmit.query.filter(BidSubmit.start_time.between(query_start, query_end)).all()
for i, bid in enumerate(bids):
    status = action[((bid.start_time - query_start).seconds) // 3600 - 8]
    bid.status = status
    bid.settlement = 0
    bid.transaction_hash = None
    bid.counterpart_name = None
    bid.counterpart_address = None
    bid.win = None
    bid.win_price = None
    bid.win_value = None

    who = random.choice([0, 1, 2, 3])
    if status == "已得標":
        bid.settlement = 0
        bid.transaction_hash = '0xb594d64485d32b009af3fbb3b456c8c7e463794af120c58eb9a3ab34de4f2543'
        bid.counterpart_name = names[who]
        bid.counterpart_address = addresses[who]
        bid.win = 1
        bid.win_price = bid.price
        bid.win_value = bid.value

    if status == "已結算":
        bid.settlement = 1
        bid.transaction_hash = '0x57ab702d3844187d8e60986c0c538612b10f41b3fc58e00b7a5e46c099db02ce'
        bid.counterpart_name = names[who]
        bid.counterpart_address = addresses[who]
        bid.win = 1
        bid.win_price = bid.price
        bid.win_value = bid.value

    if status == "執行中":
        bid.archivement = random.random()
        bid.counterpart_name = names[who]
        bid.transaction_hash = '0xb594d64485d32b009af3fbb3b456c8c7e463794af120c58eb9a3ab34de4f2543'
        bid.counterpart_address = addresses[who]
        bid.win = 1
        bid.win_price = bid.price
        bid.win_value = bid.value

    bid.update()

print("done")
