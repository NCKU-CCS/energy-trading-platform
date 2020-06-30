import sys
from argparse import ArgumentParser
from loguru import logger

from pt.simulate.config import (
    SIMULATE_FILE_PATH,
    LOG_LEVEL,
)
from pt.simulate.utils import read, find_one, send, carlab_parser, abri_parser

PARSERS = {
    "Carlab_BEMS": carlab_parser,
    "NCKU_BEMS": carlab_parser,
    "ABRI_BEMS": abri_parser,
}


def main():
    logger.remove(0)
    logger.add(sys.stderr, level=LOG_LEVEL)
    parser = ArgumentParser()
    parser.add_argument(
        "-b", "--bems", help="BEMS Name", type=str, required=True
    )
    parser.add_argument(
        "-p", "--path", help=".csv Path", type=str, default=SIMULATE_FILE_PATH, required=False
    )
    args = parser.parse_args()
    logger.info(f"Arguments: {args}")
    try:
        parse = PARSERS[args.bems]
    except KeyError:
        logger.warning(
            (
                f"No matching parser for {args.bems} BEMS, "
                "using the default parser(carlab_parser)."
            )
        )
        parse = carlab_parser

    contents = read(args.path)
    contents = parse(contents)
    result = find_one(contents)
    send(result, args.bems)


if __name__ == "__main__":
    main()
