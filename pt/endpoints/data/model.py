import uuid
from config import db

# pylint: disable=W0611
from ..address.model import History # NOQA

# pylint: enable=W0611


class Data(db.Model):
    uuid = db.Column(db.String(40), primary_key=True, unique=True, nullable=False)
    field = db.Column(db.String(120), unique=False, nullable=False)
    updated_at = db.Column(db.DateTime, unique=False, nullable=False)
    address = db.Column(db.String(120))
    # ForeignKey to History
    history_id = db.Column(db.String(80), db.ForeignKey('history.uuid'), nullable=False)
    history = db.relationship('History')
    data_type = db.Column(db.String(50))
    __mapper_args__ = {'polymorphic_identity': 'Data', 'polymorphic_on': data_type}

    def __init__(self, field, updated_at, history_id, address):
        self.uuid = str(uuid.uuid4())
        self.field = field
        self.updated_at = updated_at
        self.history_id = history_id
        self.address = address

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


class Homepage(Data):
    __tablename__ = 'homepage'
    uuid = db.Column(db.String(40), db.ForeignKey('data.uuid'), primary_key=True)
    grid = db.Column(db.Float)
    pv = db.Column(db.Float)
    building = db.Column(db.Float)
    ess = db.Column(db.Float)
    ev = db.Column(db.Float)
    __mapper_args__ = {'polymorphic_identity': 'Homepage'}

    # fmt: off
    def __init__(self, grid, pv, building, ess, ev, field, updated_at, history_id, address):
        super(Homepage, self).__init__(field, updated_at, history_id, address)
        self.grid = grid
        self.building = building
        self.ess = ess
        # pylint: disable=C0103
        self.pv = pv
        self.ev = ev
        # pylint: enable=C0103
    # fmt: on


class ESS(Data):
    __tablename__ = 'ess'
    uuid = db.Column(db.String(40), db.ForeignKey('data.uuid'), primary_key=True)
    cluster = db.Column(db.Integer)
    power_display = db.Column(db.Float)
    __mapper_args__ = {'polymorphic_identity': 'ESS'}

    def __init__(self, cluster, power_display, field, updated_at, history_id, address):
        super(ESS, self).__init__(field, updated_at, history_id, address)
        self.cluster = cluster
        self.power_display = power_display


class EV(Data):
    __tablename__ = 'ev'
    uuid = db.Column(db.String(40), db.ForeignKey('data.uuid'), primary_key=True)
    cluster = db.Column(db.Integer)
    power_display = db.Column(db.Float)
    __mapper_args__ = {'polymorphic_identity': 'EV'}

    def __init__(self, cluster, power_display, field, updated_at, history_id, address):
        super(EV, self).__init__(field, updated_at, history_id, address)
        self.cluster = cluster
        self.power_display = power_display


class PV(Data):
    __tablename__ = 'pv'
    uuid = db.Column(db.String(40), db.ForeignKey('data.uuid'), primary_key=True)
    cluster = db.Column(db.Integer)
    PAC = db.Column(db.Float)
    __mapper_args__ = {'polymorphic_identity': 'PV'}

    def __init__(self, cluster, PAC, field, updated_at, history_id, address):
        super(PV, self).__init__(field, updated_at, history_id, address)
        self.cluster = cluster
        # pylint: disable=C0103
        self.PAC = PAC
        # pylint: enable=C0103


class WT(Data):
    __tablename__ = 'wt'
    uuid = db.Column(db.String(40), db.ForeignKey('data.uuid'), primary_key=True)
    cluster = db.Column(db.Integer)
    WindGridPower = db.Column(db.Float)
    __mapper_args__ = {'polymorphic_identity': 'WT'}

    def __init__(self, cluster, WindGridPower, field, updated_at, history_id, address):
        super(WT, self).__init__(field, updated_at, history_id, address)
        self.cluster = cluster
        # pylint: disable=C0103
        self.WindGridPower = WindGridPower
        # pylint: enable=C0103
