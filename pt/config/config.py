import os
from dotenv import load_dotenv


load_dotenv()


BEMS_ACCEPT = [
    'bems_homepage_information',
    'bems_ess_display',
    'bems_ev_display',
    'bems_pv_display',
    'bems_wt_display',
]

SSL_PATH = os.environ.get('SSL_PATH', '/home/energy-trading-platform/pt/certificate/')
SSL_CONTEXT = (os.path.join(SSL_PATH, 'server.crt'), os.path.join(SSL_PATH, 'server.key'))

API_URI = os.environ.get('API_URI', 'https://nodes.thetangle.org:443').split(',')

API_OPEN = os.environ.get('API_OPEN', 'https://nodes.thetangle.org:443')

SQLALCHEMY_DATABASE_URI = os.environ.get('DB_URL', 'postgresql://dev_user:dev191026@localhost:5432/dev_db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

SEED = os.environ.get('SEED', 'OLYBZRTBYZCJXCJR9WTSHTVXJ9DTWSREFAXIAFPPEAXJAWINDFAOPCSTGVHSJQ9DJRYOUPAEZVLZKWHTZ')

DEBUG = True
TESTING = True
