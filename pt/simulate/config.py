import os

RAW_DATA_TEMPLATE = {
    "bems_homepage_information": {
        "id": "",
        "field": "",
        "grid": 0,
        "pv": 0,
        "building": 0,
        "ess": 0,
        "ev": 0,
        "updated_at": "",
    }
}
SIMULATE_FILE_PATH = os.environ.get('SIMULATE_FILE_PATH')
UPLOADER_URL = os.environ.get('UPLOADER_URL', 'http://localhost:4000/bems/upload')
HOST = os.environ.get('HOST', 'http://localhost:5000/')
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
