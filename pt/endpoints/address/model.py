from sqlalchemy.dialects.postgresql import UUID

from config import db, API

# pylint: disable=W0611
from utils.base_models import ETBaseMixin
from ..user.model import User  # NOQA

# pylint: enable=W0611


class AMI(db.Model, ETBaseMixin):
    __tablename__ = "ami"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(120))
    iota_address = db.Column(db.String(120), unique=True, nullable=False)
    time = db.Column(db.Date, unique=False, nullable=False)
    time_stamp = db.Column(db.Integer, unique=False, nullable=False)
    tag = db.Column(db.String(120), unique=True, nullable=False)
    # ForeignKey to User
    user_id = db.Column(UUID(), db.ForeignKey("user.uuid"), nullable=False)
    user = db.relationship("User")


class History(db.Model, ETBaseMixin):
    __tablename__ = "history"
    name = db.Column(db.String(80), unique=False, nullable=False)
    description = db.Column(db.String(120))
    iota_address = db.Column(db.String(120), unique=True, nullable=False)
    time = db.Column(db.Date, unique=False, nullable=False)
    time_stamp = db.Column(db.Integer, unique=False, nullable=False)
    # ForeignKey to AMI
    ami_id = db.Column(UUID(), db.ForeignKey("ami.uuid"), nullable=False)
    ami = db.relationship("AMI")


def get_address(token, time):
    ami = AMI.query.filter_by(tag=token, time=time).first()
    if ami:
        return ami
    renew(time)
    return AMI.query.filter_by(tag=token, time=time).first()


def renew(time):
    # Update Address
    new_address = API.get_new_addresses(
        index=int(time.strftime("%s")), count=AMI.query.count()
    )["addresses"]
    for amis in AMI.query.all():
        # new_address is start from index 0, but ami's id in db is start from 1
        amis.iota_address = str(new_address[amis.id - 1])
        amis.time = time
        amis.time_stamp = time.strftime("%s")
        AMI.update(amis)
        # Add to history table
        if not History.query.filter_by(ami_id=amis.uuid, time=time).first():
            history = {
                "name": amis.name,
                "description": amis.description,
                "iota_address": amis.iota_address,
                "time": amis.time,
                "time_stamp": amis.time_stamp,
                "ami_id": amis.uuid,
            }
            History.add(History(**history))
