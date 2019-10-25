import logging


logging.basicConfig(
    level=logging.DEBUG,
    format='[%(levelname)s] - %(asctime)s\n%(message)s\n' + ('-' * 70),
    datefmt='%Y-%m-%dT%H:%M:%S',
)
