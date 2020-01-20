from config import db

# pylint: disable=W0611
from utils.base_models import ETBaseMixin, UUID2STR
from ..address.model import History  # NOQA

# pylint: enable=W0611


class PowerData(db.Model, ETBaseMixin):
    __tablename__ = "powerdata"
    field = db.Column(db.String(120), unique=False, nullable=False)
    updated_at = db.Column(db.DateTime, unique=False, nullable=False)
    address = db.Column(db.String(120))
    # ForeignKey to History
    history_id = db.Column(UUID2STR, db.ForeignKey("history.uuid"), nullable=False)
    history = db.relationship("History")
    data_type = db.Column(db.String(50))
    __mapper_args__ = {"polymorphic_identity": "Data", "polymorphic_on": data_type}


class Demand(PowerData):
    __tablename__ = "demand"
    uuid = db.Column(UUID2STR, db.ForeignKey("powerdata.uuid"), primary_key=True)
    grid = db.Column(db.Float)
    pv = db.Column(db.Float)
    building = db.Column(db.Float)
    ess = db.Column(db.Float)
    ev = db.Column(db.Float)
    __mapper_args__ = {"polymorphic_identity": "Demand"}


class ESS(PowerData):
    __tablename__ = "ess"
    uuid = db.Column(UUID2STR, db.ForeignKey("powerdata.uuid"), primary_key=True)
    cluster = db.Column(db.Integer)
    power_display = db.Column(db.Float)
    __mapper_args__ = {"polymorphic_identity": "ESS"}


class EV(PowerData):
    __tablename__ = "ev"
    uuid = db.Column(UUID2STR, db.ForeignKey("powerdata.uuid"), primary_key=True)
    cluster = db.Column(db.Integer)
    power_display = db.Column(db.Float)
    __mapper_args__ = {"polymorphic_identity": "EV"}


class PV(PowerData):
    __tablename__ = "pv"
    uuid = db.Column(UUID2STR, db.ForeignKey("powerdata.uuid"), primary_key=True)
    cluster = db.Column(db.Integer)
    pac = db.Column(db.Float)
    __mapper_args__ = {"polymorphic_identity": "PV"}


class WT(PowerData):
    __tablename__ = "wt"
    uuid = db.Column(UUID2STR, db.ForeignKey("powerdata.uuid"), primary_key=True)
    cluster = db.Column(db.Integer)
    windgridpower = db.Column(db.Float)
    __mapper_args__ = {"polymorphic_identity": "WT"}
