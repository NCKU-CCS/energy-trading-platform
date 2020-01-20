from config import db
from utils.base_models import ETBaseMixin


class News(db.Model, ETBaseMixin):
    __tablename__ = "news"
    publish_time = db.Column(db.DateTime, unique=False, nullable=False)
    content = db.Column(db.String(120))
