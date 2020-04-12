from config import db
from utils.base_models import ETBaseMixin, UTCDatetime


class News(db.Model, ETBaseMixin):
    __tablename__ = "news"
    publish_time = db.Column(UTCDatetime, unique=False, nullable=False)
    content = db.Column(db.String(120))
