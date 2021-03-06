"""Models in Camper APP"""
from datetime import datetime
from marshmallow import Schema, fields
from camperapp import db
from werkzeug.security import generate_password_hash, check_password_hash
import sqlalchemy.types as types


class LowerCaseString(types.TypeDecorator):
    """Converts strings to lower case on the way in"""

    impl = types.String

    def process_bind_param(self, value, dialect):
        return value.lower()


class CampEvent(db.Model):
    """Camp Event class representing an event on the calendar"""
    __tablename__ = 'campevent'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(LowerCaseString)
    start = db.Column(db.DateTime())
    end = db.Column(db.DateTime())
    group_id = db.Column(db.Integer(), db.ForeignKey('campgroup.id'))

    def __init__(self, title, start, end):
        """
        Camp Event initializer
        :param title: title of event (string)
        :param start: Start date and time of event (datetime)
        :param end: End date and time of event (datetime)
        """
        self.title = title
        self.start = start
        self.end = end
        self.color = None

    def add_color_attr(self):
        """
        Adds a color to the camp event
        :return: None
        """
        if self.group_id is None:
            return
        self.color = self.campgroup.color

    @classmethod
    def convert_calevent_to_campevent(cls, calevent):
        """
        Converts a Full Calendar calendar event to a CampEvent
        :param calevent: Full Calendar calender event to be converted (dictionary)
        :return: CampEvent object
        """
        title = calevent['title']
        start_time =\
            CampEvent.convert_iso_datetime_to_py_datetime(calevent['start'])
        end_time =\
            CampEvent.convert_iso_datetime_to_py_datetime(calevent['end'])
        group_id = int(calevent['group_id'])

        camp_event = CampEvent(title, start_time, end_time)
        camp_event.group_id = group_id

        return camp_event

    @classmethod
    def convert_iso_datetime_to_py_datetime(cls, iso_datetime):
        """
        Converts the ISO datetime to a Python datetime
        :param iso_datetime: ISO datetime - Format - 2014-10-12T12:45
        :return: datetime object
        """
        return datetime.strptime(iso_datetime, '%Y-%m-%dT%H:%M:%S')

    @classmethod
    def convert_py_datetime_to_iso_datetime(cls, py_datetime):
        """
        Converts a Python datetime to an ISO datetime
        :param py_datetime: Python datetime object
        :return: ISO datetime string - Format: 2014-10-12T12:34
        """
        return py_datetime.strftime('%Y-%m-%dT%H:%M:%S')

    def __repr__(self):
        return '<CampEvent {}>'.format(self.title)


class CampEventSchema(Schema):
    """Schema for camp event"""
    id = fields.Int()
    title = fields.Str()
    start = fields.DateTime()
    end = fields.DateTime()
    group_id = fields.Str()
    # this doesn't original exist in db, should be appended before serialization
    color = fields.Str()


class Parent(db.Model):
    """Parent class representing a Parent of Camper(s)"""
    __tablename__ = 'parent'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(LowerCaseString)
    last_name = db.Column(LowerCaseString)
    birth_date = db.Column(db.Date())
    gender = db.Column(LowerCaseString)
    email = db.Column(LowerCaseString)
    phone = db.Column(db.String())
    street_address = db.Column(LowerCaseString)
    city = db.Column(LowerCaseString)
    state = db.Column(LowerCaseString)
    zip_code = db.Column(db.Integer())
    campers = db.relationship('Camper', backref='parent', lazy='dynamic')

    def __repr__(self):
        return '<Parent {}>'.format(self.name)


class Camper(db.Model):
    """Camper class representing a Camper"""
    __tablename__ = 'camper'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(LowerCaseString)
    last_name = db.Column(LowerCaseString)
    birth_date = db.Column(db.Date())
    grade = db.Column(db.Integer())
    gender = db.Column(LowerCaseString)
    medical_notes = db.Column(LowerCaseString)
    phone = db.Column(db.String())
    street_address = db.Column(LowerCaseString)
    city = db.Column(LowerCaseString)
    state = db.Column(LowerCaseString)
    zip_code = db.Column(db.Integer())
    is_active = db.Column(db.Boolean())
    group_id = db.Column(db.Integer(), db.ForeignKey('campgroup.id'))
    parent_id = db.Column(db.Integer(), db.ForeignKey('parent.id'))

    def age(self):
        """
        Calculate the age of a camper from Birth date
        :return: age of camper as integer
        """
        from datetime import date
        born = self.birth_date
        today = date.today()
        try:
            birthday = born.replace(year=today.year)
        except ValueError:
            # raised when birth date is February 29 and the current year is not a leap year
            birthday = born.replace(year=today.year, day=born.day - 1)
        if birthday > today:
            return today.year - born.year - 1
        else:
            return today.year - born.year

    def __repr__(self):
        return '<Camper {}, {}>'.format(self.last_name, self.first_name)


class CampGroup(db.Model):
    """Group Class representing a Group"""
    __tablename__ = 'campgroup'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    name = db.Column(LowerCaseString)
    color = db.Column(db.String())
    campers = db.relationship('Camper', backref='campgroup', lazy='dynamic')
    events = db.relationship('CampEvent', backref='campgroup', lazy='dynamic')

    def __init__(self, name, color):
        """
        CampGroup Initializer
        :param name: name of group
        :param color: color of group as hex or color string
        """
        self.name = name
        self.color = color

    def __repr__(self):
        return '<Group {}>'.format(self.name)


class Admin(db.Model):
    """Camp Administrator Model"""
    __tablename__ = 'admin'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    name = db.Column(LowerCaseString)
    email = db.Column(LowerCaseString, unique=True)
    pwdhash = db.Column(db.String())

    def __init__(self, name, email, password):
        """
        Camp Admin initializer
        :param name: name
        :param email: email address
        :param password: password - to be hashed
        """
        self.name = name
        self.email = email
        self.set_password(password)

    def set_password(self, password):
        """
        Has password and set it
        :param password: string password
        :return: None
        """
        self.pwdhash = generate_password_hash(password)

    def check_password(self, password):
        """
        Check password against hashed password
        :param password: string password
        :return: True if hash of string password is hashed password
        """
        return check_password_hash(self.pwdhash, password)
