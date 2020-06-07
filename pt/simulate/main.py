import sys
from argparse import ArgumentParser
from loguru import logger

from pt.simulate.config import SIMULATE_FILE_PATH, LOG_LEVEL
from pt.simulate.utils import read, parse, find_one, send


def main():
    logger.remove(0)
    logger.add(sys.stderr, level=LOG_LEVEL)
    parser = ArgumentParser()
    parser.add_argument(
        "-b", "--bems", help="BEMS Name", type=str, default="Carlab_BEMS"
    )
    parser.add_argument(
        "-p", "--path", help=".csv Path", type=str, default=SIMULATE_FILE_PATH
    )
    args = parser.parse_args()
    logger.info(f'Arguments: {args}')

    contents = read(args.path)
    contents = parse(contents)
    result = find_one(contents)
    send(result, args.bems)


if __name__ == "__main__":
    main()
