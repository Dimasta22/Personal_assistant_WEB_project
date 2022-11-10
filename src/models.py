from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import DateTime
from src import db

from datetime import datetime


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    nick = db.Column(db.String(30), nullable=True, unique=True)
    hash = db.Column(db.String(255), nullable=True)
    contacts = relationship('Contact', backref='users')
    notes = relationship('Note', backref='users')


class Contact(db.Model):
    __tablename__ = 'contacts'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(30), nullable=True)
    last_name = db.Column(db.String(30), nullable=True)
    birthday = db.Column(db.String(30), nullable=True)
    user_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=False)
    user = relationship('User', cascade='all, delete', backref='contact')
    emails = relationship('Email', backref='contacts')
    addresses = relationship('Address', backref='contacts')
    phones = relationship('Phone', backref='contacts')


class Email(db.Model):
    __tablename__ = 'emails'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(30), nullable=True)
    contact_id = db.Column(db.Integer, ForeignKey('contacts.id'), nullable=False)
    contact = relationship('Contact', cascade='all, delete', backref='email')


class Address(db.Model):
    __tablename__ = 'addresses'
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(250), nullable=True)
    contact_id = db.Column(db.Integer, ForeignKey('contacts.id'), nullable=False)
    contact = relationship('Contact', cascade='all, delete', backref='address')


class Phone(db.Model):
    __tablename__ = 'phones'
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20), nullable=True)
    contact_id = db.Column(db.Integer, ForeignKey('contacts.id'), nullable=False)
    contact = relationship('Contact', cascade='all, delete', backref='phone')


note_m2m_tag = db.Table(
    "note_m2m_tag",
    db.Model.metadata,
    db.Column("id", db.Integer, primary_key=True),
    db.Column("note", db.Integer, ForeignKey("notes.id")),
    db.Column("tag", db.Integer, ForeignKey("tags.id")),
)


class Note(db.Model):
    __tablename__ = "notes"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    created = db.Column(db.DateTime, default=datetime.now())
    description = db.Column(db.String(150), nullable=False)
    done = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=False)
    user = relationship('User', cascade='all, delete', backref='note')
    tags = relationship("Tag", secondary=note_m2m_tag, backref="notes")


class Tag(db.Model):
    __tablename__ = "tags"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), nullable=False, unique=True)

    def __repr__(self) -> str:
        return self.name
