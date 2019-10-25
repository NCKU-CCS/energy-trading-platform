import uuid
from config import db

from utils.base_models import ETBaseMixin


class News(db.Model, ETBaseMixin):
    __tablename__ = 'news'
    uuid = db.Column(db.String(40), primary_key=True, unique=True, nullable=False)
    publish_time = db.Column(db.DateTime, unique=False, nullable=False)
    content = db.Column(db.String(120))

    def __init__(self, publish_time, content):
        self.uuid = str(uuid.uuid4())
        self.publish_time = publish_time
        self.content = content
