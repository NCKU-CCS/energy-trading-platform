from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import text as sa_text


from config import db


class ETBaseMixin:
    uuid = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        unique=True,
        nullable=False,
        server_default=sa_text("uuid_generate_v4()"),
    )

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
