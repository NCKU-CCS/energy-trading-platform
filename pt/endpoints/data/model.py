import uuid
from config import db
from ..address.model import History

class Data(db.Model):
    uuid = db.Column(db.String(40), primary_key=True, unique=True, nullable=False)
    field = db.Column(db.String(120), unique=False, nullable=False)
    updated_at = db.Column(db.DateTime, unique=False, nullable=False)
    # ForeignKey to History
    history_id = db.Column(db.String(80), db.ForeignKey('history.uuid'), nullable=False)
    history = db.relationship('History')
    type = db.Column(db.String(50))
    __mapper_args__ = {'polymorphic_identity': 'Data', 'polymorphic_on': type}

    def __init__(self, field, updated_at, history_id):
        self.uuid = str(uuid.uuid4())
        self.field = field
        self.updated_at = updated_at
        self.history_id = history_id

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

class Homepage(Data):
    __tablename__ = 'homepage'
    uuid = db.Column(db.String(40), db.ForeignKey('data.uuid'), primary_key=True)
    grid = db.Column(db.Float)
    pv = db.Column(db.Float)
    building = db.Column(db.Float)
    ess = db.Column(db.Float)
    ev = db.Column(db.Float)
    __mapper_args__ = {'polymorphic_identity': 'Homepage'}

    def __init__(self, grid, pv, building, ess, ev, field, updated_at, history_id):
        super(Homepage, self).__init__(field, updated_at, history_id)
        self.grid = grid
        self.pv = pv
        self.building = building
        self.ess = ess
        self.ev = ev

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


class ESS(Data):
    __tablename__ = 'ess'
    uuid = db.Column(db.String(40), db.ForeignKey('data.uuid'), primary_key=True)
    cluster = db.Column(db.Integer)
    power_display = db.Column(db.Float)
    __mapper_args__ = {'polymorphic_identity': 'ESS'}

    def __init__(self, cluster, power_display, field, updated_at, history_id):
        super(ESS, self).__init__(field, updated_at, history_id)
        self.cluster = cluster
        self.power_display = power_display


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

class EV(Data):
    __tablename__ = 'ev'
    uuid = db.Column(db.String(40), db.ForeignKey('data.uuid'), primary_key=True)
    cluster = db.Column(db.Integer)
    power_display = db.Column(db.Float)
    __mapper_args__ = {'polymorphic_identity': 'EV'}

    def __init__(self, cluster, power_display, field, updated_at, history_id):
        super(EV, self).__init__(field, updated_at, history_id)
        self.cluster = cluster
        self.power_display = power_display

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

class PV(Data):
    __tablename__ = 'pv'
    uuid = db.Column(db.String(40), db.ForeignKey('data.uuid'), primary_key=True)
    cluster = db.Column(db.Integer)
    PAC = db.Column(db.Float)
    __mapper_args__ = {'polymorphic_identity': 'PV'}

    def __init__(self, cluster, PAC, field, updated_at, history_id):
        super(PV, self).__init__(field, updated_at, history_id)
        self.cluster = cluster
        self.PAC = PAC

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

class WT(Data):
    __tablename__ = 'wt'
    uuid = db.Column(db.String(40), db.ForeignKey('data.uuid'), primary_key=True)
    cluster = db.Column(db.Integer)
    WindGridPower = db.Column(db.Float)
    __mapper_args__ = {'polymorphic_identity': 'WT'}

    def __init__(self, cluster, WindGridPower, field, updated_at, history_id):
        super(WT, self).__init__(field, updated_at, history_id)
        self.cluster = cluster
        self.WindGridPower = WindGridPower

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
