from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import text as sa_text
import sqlalchemy.types as types

from config import db


# pylint: disable=W0223
class UUID2STR(types.TypeDecorator):
    impl = UUID(as_uuid=True)

    def process_result_value(self, value, dialect):
        return str(value)

# pylint: enable=W0223


class ETBaseMixin:
    uuid = db.Column(
        # UUID(as_uuid=True),
        UUID2STR,
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
