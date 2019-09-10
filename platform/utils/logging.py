import logging
split = '-'*70
logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] - [%(asctime)s]\n%(message)s\n'+split, datefmt='%Y%m%dT%H%M%S')
