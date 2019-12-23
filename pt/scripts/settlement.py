import json


# pylint: disable=C0103
json_data = {
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
# pylint: enable=C0103


def get_settlement():
    return json.dumps(json_data)
