import json
from itertools import combinations
import random
from datetime import datetime

# pylint: disable=C0103
# json_data = {
#     "date": '2019/12/09',
#     "time": '15:55',
#     "transactions": [
#         {
#             "seller": "SGESC_C_BEMS",
#             "buyer": "SGESC_D_BEMS",
#             "achievement": 0.15
#         }
#     ]
# }
# pylint: enable=C0103


def get_settlement():
    entity = ["SGESC_C_BEMS", "SGESC_D_BEMS", "Carlab_BEMS", "ABRI_BEMS"]
    achievement_list = list(range(0, 105, 5))
    tx_combination = list(combinations(entity, 2))
    transactions = []
    selected_combs = random.sample(tx_combination, k=random.randint(1, 6))
    for comb in selected_combs:
        if random.random() > 0.5:
            comb = tuple(reversed(comb))

        seller, buyer = comb
        transactions.append({
            "seller": seller,
            "buyer": buyer,
            "achievement": random.choice(achievement_list) / 100
        })

    now = datetime.now()
    data = {
        "date": now.strftime("%Y/%m/%d"),
        "time": now.strftime("%H/%M"),
        "transactions": transactions
    }

    return json.dumps(data)
