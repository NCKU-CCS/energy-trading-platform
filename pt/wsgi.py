import os

from dotenv import load_dotenv

from app import create_app


load_dotenv()
# pylint: disable=C0103
# invalid-name
app = create_app(os.environ.get('APP_SETTINGS', 'production'))

if __name__ == '__main__':
    app.run()
# pylint: enable=C0103
