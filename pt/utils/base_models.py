import datetime

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import text as sa_text
import sqlalchemy.types as types

from config import db, TZ


# pylint: disable=W0223, W0613, R0201
class UTCDatetime(types.TypeDecorator):
    impl = types.TIMESTAMP

    def process_bind_param(self, value, dialect):
        """change timezone before insert to db"""
        return (
            value.astimezone(datetime.timezone.utc).replace(tzinfo=None)
            if value
            else None
        )

    def process_result_value(self, value, dialect):
        """change timezone after select from db"""
        return (
            value.replace(tzinfo=datetime.timezone.utc)
            .astimezone(TZ)
            .replace(tzinfo=None)
            if value
            else None
        )


class UTCDate(types.TypeDecorator):
    impl = types.DATE


class UUID2STR(types.TypeDecorator):
    impl = UUID(as_uuid=True)

    def process_result_value(self, value, dialect):
        return str(value)


# pylint: enable=W0223, W0613, R0201


class ETBaseMixin:
    uuid = db.Column(
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

    # pylint: disable=R0201
    def rollback(self):
        db.session.rollback()

    # pylint: enable=R0201

    def __repr__(self):
        return self.uuid
