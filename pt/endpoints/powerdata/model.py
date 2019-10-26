from config import db

# pylint: disable=W0611
from utils.base_models import ETBaseMixin
from ..address.model import History # NOQA

# pylint: enable=W0611


class PowerData(db.Model, ETBaseMixin):
    __tablename__ = 'powerdata'
    uuid = db.Column(db.String(40), primary_key=True, unique=True, nullable=False)
    field = db.Column(db.String(120), unique=False, nullable=False)
    updated_at = db.Column(db.DateTime, unique=False, nullable=False)
    address = db.Column(db.String(120))
    # ForeignKey to History
    history_id = db.Column(db.String(80), db.ForeignKey('history.uuid'), nullable=False)
    history = db.relationship('History')
    data_type = db.Column(db.String(50))
    __mapper_args__ = {'polymorphic_identity': 'Data', 'polymorphic_on': data_type}

    def __init__(self, data_struct):
        self.uuid = data_struct['uuid']
        self.field = data_struct['field']
        self.updated_at = data_struct['updated_at']
        self.history_id = data_struct['history_id']
        self.address = data_struct['address']


class Demand(PowerData):
    __tablename__ = 'demand'
    uuid = db.Column(db.String(40), db.ForeignKey('powerdata.uuid'), primary_key=True)
    grid = db.Column(db.Float)
    pv = db.Column(db.Float)
    building = db.Column(db.Float)
    ess = db.Column(db.Float)
    ev = db.Column(db.Float)
    __mapper_args__ = {'polymorphic_identity': 'Demand'}

    # fmt: off
    def __init__(self, data_struct, history_id, address):
        mother = {
            'uuid': data_struct['id'],
            'field': data_struct['field'],
            'updated_at': data_struct['updated_at'],
            'history_id': history_id,
            'address': address,
        }
        super(Demand, self).__init__(mother)
        self.grid = data_struct['grid']
        self.building = data_struct['building']
        self.ess = data_struct['ess']
        # pylint: disable=C0103
        self.pv = data_struct['pv']
        self.ev = data_struct['ev']
        # pylint: enable=C0103
    # fmt: on


class ESS(PowerData):
    __tablename__ = 'ess'
    uuid = db.Column(db.String(40), db.ForeignKey('powerdata.uuid'), primary_key=True)
    cluster = db.Column(db.Integer)
    power_display = db.Column(db.Float)
    __mapper_args__ = {'polymorphic_identity': 'ESS'}

    def __init__(self, data_struct, history_id, address):
        mother = {
            'uuid': data_struct['id'],
            'field': data_struct['field'],
            'updated_at': data_struct['updated_at'],
            'history_id': history_id,
            'address': address,
        }
        super(ESS, self).__init__(mother)
        self.cluster = data_struct['cluster']
        self.power_display = data_struct['power_display']


class EV(PowerData):
    __tablename__ = 'ev'
    uuid = db.Column(db.String(40), db.ForeignKey('powerdata.uuid'), primary_key=True)
    cluster = db.Column(db.Integer)
    power_display = db.Column(db.Float)
    __mapper_args__ = {'polymorphic_identity': 'EV'}

    def __init__(self, data_struct, history_id, address):
        mother = {
            'uuid': data_struct['id'],
            'field': data_struct['field'],
            'updated_at': data_struct['updated_at'],
            'history_id': history_id,
            'address': address,
        }
        super(EV, self).__init__(mother)
        self.cluster = data_struct['cluster']
        self.power_display = data_struct['power']


class PV(PowerData):
    __tablename__ = 'pv'
    uuid = db.Column(db.String(40), db.ForeignKey('powerdata.uuid'), primary_key=True)
    cluster = db.Column(db.Integer)
    pac = db.Column(db.Float)
    __mapper_args__ = {'polymorphic_identity': 'PV'}

    def __init__(self, data_struct, history_id, address):
        mother = {
            'uuid': data_struct['id'],
            'field': data_struct['field'],
            'updated_at': data_struct['updated_at'],
            'history_id': history_id,
            'address': address,
        }
        super(PV, self).__init__(mother)
        self.cluster = data_struct['cluster']
        # pylint: disable=C0103
        self.pac = data_struct['PAC']
        # pylint: enable=C0103


class WT(PowerData):
    __tablename__ = 'wt'
    uuid = db.Column(db.String(40), db.ForeignKey('powerdata.uuid'), primary_key=True)
    cluster = db.Column(db.Integer)
    windgridpower = db.Column(db.Float)
    __mapper_args__ = {'polymorphic_identity': 'WT'}

    def __init__(self, data_struct, history_id, address):
        mother = {
            'uuid': data_struct['id'],
            'field': data_struct['field'],
            'updated_at': data_struct['updated_at'],
            'history_id': history_id,
            'address': address,
        }
        super(WT, self).__init__(mother)
        self.cluster = data_struct['cluster']
        # pylint: disable=C0103
        self.WindGridPower = data_struct['WindGridPower']
        # pylint: enable=C0103
