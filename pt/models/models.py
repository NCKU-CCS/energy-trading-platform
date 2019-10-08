from config import app, db

'''
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(pjdir, 'data.db')
db = SQLAlchemy(app)
'''


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(40), unique=True, nullable=False)
    account = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    username = db.Column(db.String(80), unique=False, nullable=False)
    tag = db.Column(db.String(120), unique=True, nullable=False)  # Login Bearer Tag
    avatar = db.Column(db.String(120))
    balance = db.Column(db.Integer)
    address = db.Column(db.String(120))
    ETH_address = db.Column(db.String(80))
    # Association to AMI
    amis = db.relationship('AMI', backref='User', lazy='dynamic')
    # Association to Bid
    bids = db.relationship('Bid', backref='User', lazy='dynamic')


class AMI(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(40), unique=True, nullable=False)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(120))
    IOTA_address = db.Column(db.String(120), unique=True, nullable=False)
    time = db.Column(db.Date, unique=False, nullable=False)
    time_stamp = db.Column(db.Integer, unique=False, nullable=False)
    tag = db.Column(db.String(120), unique=True, nullable=False)
    # ForeignKey to User
    user_id = db.Column(db.String(80), db.ForeignKey('User.id'), nullable=False)
    # Association to History
    historys = db.relationship('History', backref='AMI', lazy='dynamic')

    # def __init__(self, name, address, time):
    #     self.name = name
    #     self.address = address
    #     self.time = time
    #     self.time_stamp = time.strftime("%s")

    # def add_field(self):
    #     db.session.add(self)
    #     db.session.commit()

    # def update_field(self):
    #     db.session.commit()

    # def delete_field(self):
    #     db.session.delete(self)
    #     db.session.commit()

    # @classmethod
    # def find(cls, name, time):
    #     return cls.query.filter_by(name = name, time = time).first()

    # @classmethod
    # def find_by_name(cls, name):
    #     return cls.query.filter_by(name = name).first()

    # def __repr__(self):
    #     return self.address


class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(40), unique=True, nullable=False)
    name = db.Column(db.String(80), unique=False, nullable=False)
    IOTA_address = db.Column(db.String(120), unique=True, nullable=False)
    time = db.Column(db.Date, unique=False, nullable=False)
    time_stamp = db.Column(db.Integer, unique=False, nullable=False)
    # ForeignKey to AMI
    ami_id = db.Column(db.String(80), db.ForeignKey('AMI.id'), nullable=False)
    # Association to Data
    datas = db.relationship('Data', backref='History', lazy='dynamic')

    # def __init__(self, name, address, time):
    #     self.name = name
    #     self.address = address
    #     self.time = time
    #     self.time_stamp = time.strftime("%s")

    # def add_field(self):
    #     db.session.add(self)
    #     db.session.commit()

    # def update_field(self):
    #     db.session.commit()

    # def delete_field(self):
    #     db.session.delete(self)
    #     db.session.commit()

    # @classmethod
    # def find(cls, name, time):
    #     return cls.query.filter_by(name = name, time = time).first()

    # # @classmethod
    # # def find_by_name(cls, name):
    # #     return cls.query.filter_by(name = name).first()

    # def __repr__(self):
    #     return self.address


# class UploaderModel(db.Model):
#     __tablename__ = 'uploader'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(80), unique=True, nullable=False)
#     tag = db.Column(db.String(120), unique=True, nullable=False)

#     def __init__(self, name, tag):
#         self.name = name
#         self.tag = tag

#     def add_uploader(self):
#         db.session.add(self)
#         db.session.commit()

#     def update_uploader(self):
#         db.session.commit()

#     def delete_uploader(self):
#         db.session.delete(self)
#         db.session.commit()

#     @classmethod
#     def find(cls, name, tag):
#         return cls.query.filter_by(name = name, tag = tag).first()

#     @classmethod
#     def find_by_tag(cls, tag):
#         return cls.query.filter_by(tag = tag).first()

#     def __repr__(self):
#         return self.name


class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(40), unique=True, nullable=False)
    field = db.Column(db.String(120), unique=False, nullable=False)
    updated_at = db.Column(db.Date, unique=False, nullable=False)
    # ForeignKey to History
    history_id = db.Column(db.String(80), db.ForeignKey('History.id'), nullable=False)
    type = db.Column(db.String(50))
    __mapper_args__ = {'polymorphic_identity': 'Data', 'polymorphic_on': type}


class Homepage(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('Data.id'), primary_key=True)
    grid = db.Column(db.Float)
    pv = db.Column(db.Float)
    building = db.Column(db.Float)
    ess = db.Column(db.Float)
    ev = db.Column(db.Float)
    __mapper_args__ = {'polymorphic_identity': 'Homepage'}


class ESS(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('Data.id'), primary_key=True)
    cluster = db.Column(db.Integer)
    power_display = db.Column(db.Float)
    __mapper_args__ = {'polymorphic_identity': 'ESS'}


class EV(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('Data.id'), primary_key=True)
    cluster = db.Column(db.Integer)
    power = db.Column(db.Float)
    __mapper_args__ = {'polymorphic_identity': 'EV'}


class PV(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('Data.id'), primary_key=True)
    cluster = db.Column(db.Integer)
    PAC = db.Column(db.Float)
    __mapper_args__ = {'polymorphic_identity': 'PV'}


class WT(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('Data.id'), primary_key=True)
    cluster = db.Column(db.Integer)
    WindGridPower = db.Column(db.Float)
    __mapper_args__ = {'polymorphic_identity': 'WT'}


class Bid(db.Column):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(40), unique=True, nullable=False)
    type = db.Column(db.String(40))  # sell or buy
    time = db.Column(db.Date, unique=False, nullable=False)
    win = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(40))
    counterpart_name = db.Column(db.String(80))
    counterpart_address = db.Column(db.String(120))
    bid_value = db.Column(db.Float)
    bid_price = db.Column(db.Float)
    win_value = db.Column(db.Float)
    win_price = db.Column(db.Float)
    achievement = db.Column(db.Float)
    settlement = db.Column(db.Float)
    transaction_hash = db.Column(db.String(80))
    upload = db.Column(db.Date, unique=False, nullable=False)
    # ForeignKey to User
    user_id = db.Column(db.String(80), db.ForeignKey('User.id'), nullable=False)
    # Association to Submit
    submits = db.relationship('Submit', backref='Bid', lazy='dynamic')


class Submit(db.Column):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(40), unique=True, nullable=False)
    type = db.Column(db.String(40))  # sell or buy
    time = db.Column(db.Date, unique=False, nullable=False)
    value = db.Column(db.Float)
    price = db.Column(db.Float)
    upload_time = db.Column(db.Date, unique=False, nullable=False)
    # ForeignKey to Bid
    bid_id = db.Column(db.String(80), db.ForeignKey('Bid.id'), nullable=False)


class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(40), unique=True, nullable=False)
    publish_time = db.Column(db.Date, unique=False, nullable=False)
    content = db.Column(db.String(120))
