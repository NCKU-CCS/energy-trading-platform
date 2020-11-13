import os

from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from config import db
from app import create_app


def init_manager():
    config_name = os.environ.get("APP_SETTINGS", "development")
    app = create_app(config_name)
    Migrate(app, db)
    manager = Manager(app)
    manager.add_command('db', MigrateCommand)
    manager.run()


if __name__ == '__main__':
    init_manager()
