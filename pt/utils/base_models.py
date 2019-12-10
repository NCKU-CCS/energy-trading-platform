from config import db


class ETBaseMixin:
    def add(self):
        db.session.add(self)
        db.session.commit()

    # pylint: disable=R0201
    def update(self):
        db.session.commit()

    # pylint: enable=R0201

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return self.uuid
