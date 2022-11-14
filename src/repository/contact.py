from src import db
from src import models
from sqlalchemy import and_, func
import time

def get_contacts_user(user_id):
    return db.session.query(models.Contact).where(models.Contact.user_id == user_id).all()

def get_contacts_user_by_id(user_id, contact_id):
    return db.session.query(models.Contact).filter(
        and_(models.Contact.user_id == int(user_id), models.Contact.id == int(contact_id))).first()


def create_contact(first_name, last_name, birthday, email, address, phone, user_id):
    contact = models.Contact(first_name=first_name, last_name=last_name, birthday=birthday, user_id=user_id)
    db.session.add(contact)
    db.session.commit()
    if email:
        add_email(email=email, contact_id=contact.id)
    if address:
        add_address(address=address, contact_id=contact.id)
    if phone:
        add_phone(phone=phone.replace(" ", ""), contact_id=contact.id)
    return contact

def add_email(contact_id, email):
    email = models.Email(contact_id=contact_id, email=email)
    db.session.add(email)
    db.session.commit()
    return email

def add_address(contact_id, address):
    address = models.Address(contact_id=contact_id, address=address)
    db.session.add(address)
    db.session.commit()
    return address

def add_phone(contact_id, phone):
    phone = models.Phone(contact_id=contact_id, phone=phone.replace(" ", ""))
    db.session.add(phone)
    db.session.commit()
    return phone

def cont_delete(contact_id, user_id):
    contact = get_contacts_user_by_id(user_id, contact_id)
    db.session.query(models.Contact).filter(
        and_(models.Contact.user_id == int(user_id), models.Contact.id == int(contact_id))).delete()
        
    # print("address = ",contact.addresses)
    
    # for email in contact.emails:
    #     email_delete(email)
    
    # for address in contact.addresses:
    #     # print("address = ", address.id)
    #     address_delete(address)
    
    # for phone in contact.phones:
    #     # print("phone = ", phone)
    #     phone_delete(phone)

    
    db.session.commit()

def email_delete(email):
    db.session.query(models.Email).filter(models.Email.id == int(email.id)).delete()

def phone_delete(phone):
    db.session.query(models.Phone).filter(models.Phone.id == int(phone.id)).delete()

def address_delete(address):
    db.session.query(models.Address).filter(models.Address.id == int(address.id)).delete()

def get_email(contact_id, email_id):
    email_ses = db.session.query(models.Email).filter(
            and_(models.Email.contact_id == int(contact_id), models.Email.id == int(email_id))).all()
    return email_ses

def get_phone(contact_id, phone_id):
    phone_ses = db.session.query(models.Phone).filter(
            and_(models.Phone.contact_id == int(contact_id), models.Phone.id == int(phone_id))).all()
    return phone_ses

def get_address(contact_id, address_id):
    address_ses = db.session.query(models.Address).filter(
        and_(models.Address.contact_id == int(contact_id), models.Address.id == int(address_id))).all()
    return address_ses

def update_first_name(contact_id, user_id, first_name):
    if first_name != '':
        contact = get_contacts_user_by_id(user_id, contact_id)
        contact.first_name = first_name
        db.session.commit()

def update_last_name(contact_id, user_id, last_name):
    if last_name != '':
        contact = get_contacts_user_by_id(user_id, contact_id)
        contact.last_name = last_name
        db.session.commit()

def update_birthday(contact_id, user_id, birthday):
    if birthday != '':
        contact = get_contacts_user_by_id(user_id, contact_id)
        contact.birthday = birthday
        db.session.commit()

def update_email(contact_id, email_id, email):
    if email != '':
        email_ses = get_email(contact_id, email_id)
        email_ses[0].email = email
        db.session.commit()

def update_phone(contact_id, phone_id, phone):
    if phone != '':
        phone_ses = get_phone(contact_id, phone_id)
        phone_ses[0].phone = phone
        db.session.commit()

def update_address(contact_id, address_id, address):
    if address != '':
        address_ses = get_address(contact_id, address_id)
        address_ses[0].address = address
        db.session.commit()




