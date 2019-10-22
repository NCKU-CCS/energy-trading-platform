import uuid
from config import db, API
from generate_address import get_addresses

# pylint: disable=W0611
from ..user.model import User # NOQA

# pylint: enable=W0611


class AMI(db.Model):
    __tablename__ = 'ami'
    sn = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    uuid = db.Column(db.String(40), primary_key=True, unique=True, nullable=False)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(120))
    iota_address = db.Column(db.String(120), unique=True, nullable=False)
    time = db.Column(db.Date, unique=False, nullable=False)
    time_stamp = db.Column(db.Integer, unique=False, nullable=False)
    tag = db.Column(db.String(120), unique=True, nullable=False)
    # ForeignKey to User
    user_id = db.Column(db.String(40), db.ForeignKey('user.uuid'), nullable=False)
    user = db.relationship('User')

    def __init__(self, name, description, iota_address, time, tag, user_id):
        # pylint: disable=C0103
        self.sn = AMI.query.count()
        # pylint: enable=C0103
        self.uuid = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.iota_address = iota_address
        self.time = time
        self.time_stamp = time.strftime("%s")
        self.tag = tag
        self.user_id = user_id

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


class History(db.Model):
    __tablename__ = 'history'
    uuid = db.Column(db.String(40), primary_key=True, unique=True, nullable=False)
    name = db.Column(db.String(80), unique=False, nullable=False)
    description = db.Column(db.String(120))
    iota_address = db.Column(db.String(120), unique=True, nullable=False)
    time = db.Column(db.Date, unique=False, nullable=False)
    time_stamp = db.Column(db.Integer, unique=False, nullable=False)
    # ForeignKey to AMI
    ami_id = db.Column(db.String(40), db.ForeignKey('ami.uuid'), nullable=False)
    ami = db.relationship("AMI")

    def __init__(self, name, description, iota_address, time, ami_id):
        self.uuid = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.iota_address = iota_address
        self.time = time
        self.time_stamp = time.strftime("%s")
        self.ami_id = ami_id

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


def address(token, time):
    ami = AMI.query.filter_by(tag=token, time=time).first()
    if ami:
        return ami
    renew(time)
    return AMI.query.filter_by(tag=token, time=time).first()


def renew(time):
    # Update Address
    new_address = get_addresses(int(time.strftime("%s")), AMI.query.count())
    new_address = API.get_new_addresses(
        index=int(time.strftime("%s")), count=AMI.query.count()
    )['addresses']
    for amis in AMI.query.all():
        amis.iota_address = str(new_address[amis.sn])
        amis.time = time
        amis.time_stamp = time.strftime("%s")
        AMI.update(amis)
        # Add to history table
        if not History.query.filter_by(ami_id=amis.uuid, time=time).first():
            History.add(
                History(
                    amis.name, amis.description, amis.iota_address, amis.time, amis.uuid
                )
            )
