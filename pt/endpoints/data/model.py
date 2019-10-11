from config import db
from ..address.model import History

class Data(db.Model):
    uuid = db.Column(db.String(40), primary_key=True, unique=True, nullable=False)
    field = db.Column(db.String(120), unique=False, nullable=False)
    updated_at = db.Column(db.Date, unique=False, nullable=False)
    # ForeignKey to History
    history_id = db.Column(db.String(80), db.ForeignKey('history.uuid'), nullable=False)
    history = db.relationship('History')
    type = db.Column(db.String(50))
    __mapper_args__ = {'polymorphic_identity': 'Data', 'polymorphic_on': type}


class Homepage(Data):
    __tablename__ = 'homepage'
    uuid = db.Column(db.Integer, db.ForeignKey('data.uuid'), primary_key=True)
    grid = db.Column(db.Float)
    pv = db.Column(db.Float)
    building = db.Column(db.Float)
    ess = db.Column(db.Float)
    ev = db.Column(db.Float)
    __mapper_args__ = {'polymorphic_identity': 'Homepage'}


class ESS(Data):
    __tablename__ = 'ess'
    uuid = db.Column(db.Integer, db.ForeignKey('data.uuid'), primary_key=True)
    cluster = db.Column(db.Integer)
    power_display = db.Column(db.Float)
    __mapper_args__ = {'polymorphic_identity': 'ESS'}


class EV(Data):
    __tablename__ = 'ev'
    uuid = db.Column(db.Integer, db.ForeignKey('data.uuid'), primary_key=True)
    cluster = db.Column(db.Integer)
    power = db.Column(db.Float)
    __mapper_args__ = {'polymorphic_identity': 'EV'}


class PV(Data):
    __tablename__ = 'pv'
    uuid = db.Column(db.Integer, db.ForeignKey('data.uuid'), primary_key=True)
    cluster = db.Column(db.Integer)
    PAC = db.Column(db.Float)
    __mapper_args__ = {'polymorphic_identity': 'PV'}


class WT(Data):
    __tablename__ = 'wt'
    uuid = db.Column(db.Integer, db.ForeignKey('data.uuid'), primary_key=True)
    cluster = db.Column(db.Integer)
    WindGridPower = db.Column(db.Float)
    __mapper_args__ = {'polymorphic_identity': 'WT'}
