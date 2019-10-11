import uuid
from config import db


class News(db.Model):
    __tablename__ = 'news'
    uuid = db.Column(db.String(40), primary_key=True, unique=True, nullable=False)
    publish_time = db.Column(db.DateTime, unique=False, nullable=False)
    content = db.Column(db.String(120))

    def __init__(self, publish_time, content):
        self.uuid = str(uuid.uuid4())
        self.publish_time = publish_time
        self.content = content

    def add(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return self.uuid
