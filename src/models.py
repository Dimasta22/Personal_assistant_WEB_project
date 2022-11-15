from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import DateTime
from src import db

from datetime import datetime


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    nick = db.Column(db.String(30), nullable=True, unique=True)
    hash = db.Column(db.String(255), nullable=True)
    contacts = relationship("Contact", back_populates="user",
                            cascade="all, delete",
                            passive_deletes=True, )
    notes = relationship("Note", back_populates="user",
                         cascade="all, delete",
                         passive_deletes=True, )


class Contact(db.Model):
    __tablename__ = "contact"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(30), nullable=True)
    last_name = db.Column(db.String(30), nullable=True)
    birthday = db.Column(db.String(30), nullable=True)
    user_id = db.Column(db.Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    user = relationship("User", back_populates="contacts")
    emails = relationship("Email", back_populates="contact",
                          cascade="all, delete",
                          passive_deletes=True, )
    addresses = relationship("Address", back_populates="contact",
                             cascade="all, delete",
                             passive_deletes=True, )
    phones = relationship("Phone", back_populates="contact",
                          cascade="all, delete",
                          passive_deletes=True, )


class Email(db.Model):
    __tablename__ = "emails"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(30), nullable=True)
    contact_id = db.Column(db.Integer, ForeignKey("contact.id", ondelete="CASCADE"), nullable=False)
    contact = relationship("Contact", back_populates="emails")


class Address(db.Model):
    __tablename__ = "addresses"
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(250), nullable=True)
    contact_id = db.Column(db.Integer, ForeignKey("contact.id", ondelete="CASCADE"), nullable=False)
    contact = relationship("Contact", back_populates="addresses")


class Phone(db.Model):
    __tablename__ = "phones"
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20), nullable=True)
    contact_id = db.Column(db.Integer, ForeignKey("contact.id", ondelete="CASCADE"), nullable=False)
    contact = relationship("Contact", back_populates="phones")


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
    user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
    user = relationship('User', cascade='all, delete', backref='note')
    tags = relationship("Tag", secondary=note_m2m_tag, backref="notes")


class Tag(db.Model):
    __tablename__ = "tags"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), nullable=False, unique=True)
    user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)

    def repr(self) -> str:
        return self.name


class File(db.Model):
    __tablename__ = 'files'
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(350), unique=True, nullable=False)
    description = db.Column(db.String(300), nullable=False)
    size = db.Column(db.Integer, nullable=False)
    type_id = db.Column(db.Integer, ForeignKey('filetypes.id'), nullable=False)
    file_type = relationship('FileType', cascade='all, delete')
    user_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=False)
    user = relationship('User', cascade='all, delete', backref='files')


class FileType(db.Model):
    __tablename__ = 'filetypes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), nullable=False, unique=True)
    files = relationship('File')
