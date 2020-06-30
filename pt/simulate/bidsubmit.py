import sys
from datetime import datetime
from argparse import ArgumentParser
from loguru import logger
import pytz

from pt.simulate.config import (
    SIMULATE_FILE_PATH,
    LOG_LEVEL,
    UPLOAD_TZ
)
from pt.simulate.utils import auth, bidsubmit, daterange_hours, pairwise, convert_time_zone


def main():
    logger.remove(0)
    logger.add(sys.stderr, level=LOG_LEVEL)
    parser = ArgumentParser()
    parser.add_argument(
        "-a", "--account", help="account", type=str, required=True
    )
    parser.add_argument(
        "-p", "--password", help="password", type=str, required=True
    )
    parser.add_argument(
        "-t", "--bid_type", help="Bidding Type", type=str, required=True
    )
    parser.add_argument(
        "-s", "--start_time", help="Bidding Start Time", type=str, required=True
    )
    parser.add_argument(
        "-e", "--end_time", help="Bidding End Time", type=str, required=True
    )
    parser.add_argument(
        "-v", "--value", help="Bidding Value", type=float, required=True
    )
    parser.add_argument(
        "-m", "--price", help="Bidding Price Per kWh", type=float, required=True
    )
    args = parser.parse_args()
    logger.info(f"Arguments: {args}")

    token = auth(args.account, args.password)
    logger.debug(f"Token: {token}")

    submit_args = vars(args)
    submit_args.pop('account')
    submit_args.pop('password')

    start_time = convert_time_zone(
        datetime.strptime(args.start_time, "%Y/%m/%d %H"),
        pytz.utc,
        UPLOAD_TZ
    )
    end_time = convert_time_zone(
        datetime.strptime(args.end_time, "%Y/%m/%d %H"),
        pytz.utc,
        UPLOAD_TZ
    )

    for st, et in pairwise(daterange_hours(start_time, end_time)):
        submit_args["start_time"] = st.strftime('%Y/%m/%d %H')
        submit_args["end_time"] = et.strftime('%Y/%m/%d %H')

        bidsubmit(token=token, **submit_args)
    

if __name__ == "__main__":
    main()
