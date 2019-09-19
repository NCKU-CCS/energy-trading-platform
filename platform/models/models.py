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

class FieldModel(db.Model):
    __tablename__ = 'today'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    address = db.Column(db.String(120), unique=True, nullable=False)
    time = db.Column(db.Date, unique=False, nullable=False)
    time_stamp = db.Column(db.Integer, unique=False, nullable=False)

    def __init__(self, name, address, time):
        self.name = name
        self.address = address
        self.time = time
        self.time_stamp = time.strftime("%s")

    def add_field(self):
        db.session.add(self)
        db.session.commit()

    def update_field(self):
        db.session.commit()

    def delete_field(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find(cls, name, time):
        return cls.query.filter_by(name = name, time = time).first()

    @classmethod
    def find_by_name(cls, name):
        return cls.query.filter_by(name = name).first()

    def __repr__(self):
        return self.address

class HistoryModel(db.Model):
    __tablename__ = 'history'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    address = db.Column(db.String(120), unique=True, nullable=False)
    time = db.Column(db.Date, unique=False, nullable=False)
    time_stamp = db.Column(db.Integer, unique=False, nullable=False)

    def __init__(self, name, address, time):
        self.name = name
        self.address = address
        self.time = time
        self.time_stamp = time.strftime("%s")

    def add_field(self):
        db.session.add(self)
        db.session.commit()

    def update_field(self):
        db.session.commit()

    def delete_field(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find(cls, name, time):
        return cls.query.filter_by(name = name, time = time).first()

    # @classmethod
    # def find_by_name(cls, name):
    #     return cls.query.filter_by(name = name).first()

    def __repr__(self):
        return self.address

class UploaderModel(db.Model):
    __tablename__ = 'uploader'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    tag = db.Column(db.String(120), unique=True, nullable=False)

    def __init__(self, name, tag):
        self.name = name
        self.tag = tag

    def add_uploader(self):
        db.session.add(self)
        db.session.commit()

    def update_uploader(self):
        db.session.commit()

    def delete_uploader(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find(cls, name, tag):
        return cls.query.filter_by(name = name, tag = tag).first()

    @classmethod
    def find_by_tag(cls, tag):
        return cls.query.filter_by(tag = tag).first()

    def __repr__(self):
        return self.name