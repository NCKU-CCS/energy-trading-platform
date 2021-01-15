import sys
import json
import random

from datetime import datetime, time

sys.path.insert(0, "./")

# pylint: disable=C0413
from endpoints.bid.model import BidSubmit  # noqa: E402

# pylint: enable=C0413


def get_settlement():
    """ This function generates test settlement data for front-end,
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
    achievement_list = list(range(0, 105, 5))

    # Transactions are fixed for the test
    transactions = [
        {
            "seller": "Carlab_BEMS",
            "buyer": "SGESC_C_BEMS",
            "achievement": random.choice(achievement_list) / 100,
        },
        {
            "seller": "SGESC_D_BEMS",
            "buyer": "SGESC_C_BEMS",
            "achievement": random.choice(achievement_list) / 100,
        },
        {
            "seller": "SGESC_C_BEMS",
            "buyer": "ABRI_BEMS",
            "achievement": random.choice(achievement_list) / 100,
        },
    ]
    now = datetime.utcnow()
    data = {
        "date": now.strftime("%Y/%m/%d"),
        "time": now.strftime("%H:%M"),
        "transactions": transactions,
    }

    return json.dumps(data)


def simulate_achievement():
    """ This function generates test settlement data for front-end,
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
    now = datetime.now()
    start_time = datetime.combine(now.date(), time(now.hour, 0))
    bids = (
        BidSubmit.query.filter_by(
            status="執行中",
            bid_type="sell",
            start_time=start_time,
        ).all()
    )
    transactions = []
    for bid in bids:
        transaction = {}
        transaction["seller"] = bid.tenders.user.username
        transaction["buyer"] = bid.counterpart_name
        counter_bid = (
            BidSubmit.query.filter_by(
                status="執行中",
                start_time=start_time,
                win_value=bid.win_value,
                counterpart_name=bid.tenders.user.username,
            ).first()
        )
        if counter_bid:
            if bid.achievement is None:
                bid.achievement = 0
                counter_bid.achievement = 0
            else:
                # progessive increase
                achievement = bid.achievement
                achievement += (random.random() * (1 - achievement))
                bid.achievement = achievement
                counter_bid.achievement = achievement
            transaction["achievement"] = bid.achievement
            # update value
            bid.update()
            counter_bid.update()
            transactions.append(transaction)

    now = datetime.utcnow()
    data = {
        "date": now.strftime("%Y/%m/%d"),
        "time": now.strftime("%H:%M"),
        "transactions": transactions,
    }
    return json.dumps(data)
