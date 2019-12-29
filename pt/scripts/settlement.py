import json
import random
from datetime import datetime


def get_settlement():
    achievement_list = list(range(0, 105, 5))
    transactions = [
        {
            "seller": "Carlab_BEMS",
            "buyer": "SGESC_C_BEMS",
            "achievement": random.choice(achievement_list) / 100
        },
        {
            "seller": "SGESC_D_BEMS",
            "buyer": "SGESC_C_BEMS",
            "achievement": random.choice(achievement_list) / 100
        },
        {
            "seller": "SGESC_C_BEMS",
            "buyer": "ABRI_BEMS",
            "achievement": random.choice(achievement_list) / 100
        }
    ]
    now = datetime.now()
    data = {
        "date": now.strftime("%Y/%m/%d"),
        "time": now.strftime("%H:%M"),
        "transactions": transactions
    }

    return json.dumps(data)
