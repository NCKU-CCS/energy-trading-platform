import json
import random
from datetime import datetime


""" This function generates test settlement data for frond-end,
    current ET users are mapped as below:

    智駕車BEMS=> Carlab_BEMS
    沙崙綠能科學城C區BEMS=> SGESC_C_BEMS
    沙崙綠能科學城D區BEMS=> SGESC_D_BEMS
    歸仁校區建研所BEMS => ABRI_BEMS

    Data sample:
    {
        "date": '2019/12/09',
        "time": '15:55',
        "transactions": [
            {
                "seller": "SGESC_C_BEMS",
                "buyer": "SGESC_D_BEMS",
                "achievement": 0.15
            }
        ]
    }
"""
def get_settlement():
    achievement_list = list(range(0, 105, 5))

    # Transactions are fixed for the test
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
