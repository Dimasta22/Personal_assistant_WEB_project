from src import db
from src import models
from sqlalchemy import and_, func
from datetime import datetime
import difflib

def get_contacts_user(user_id):
    return db.session.query(models.Contact).where(models.Contact.user_id == user_id).all()


def get_contacts_user_by_id(user_id, contact_id):
    return db.session.query(models.Contact).filter(
        and_(models.Contact.user_id == int(user_id), models.Contact.id == int(contact_id))).first()


def create_contact(first_name, last_name, birthday, email, address, phone, user_id):
    contact = models.Contact(
        first_name=first_name, last_name=last_name, birthday=birthday, user_id=user_id)
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
    db.session.commit()


def find_contact_birthday(user_id, birthday):
    contacts = get_contacts_user(user_id=user_id)
    birthday = datetime.strptime(birthday, "%Y-%m-%d")
    if birthday > datetime(year=datetime.now().year+1, month=datetime.now().month, day=datetime.now().day):
        birthday = datetime(year=datetime.now().year+1, month=datetime.now().month, day=datetime.now().day)
    new_contacts = []
    for contact in contacts:
        if contact.birthday == '-' or contact.birthday == '':
            continue
        contact_birthday = datetime.strptime(contact.birthday, "%d.%m.%Y")
        contact_birthday = datetime(year=datetime.now().year,
                        month=contact_birthday.month, day=contact_birthday.day)
        if datetime.now().month > contact_birthday.month:
            contact_birthday = datetime(year=datetime.now().year+1,
                        month=contact_birthday.month, day=contact_birthday.day)
        if contact_birthday - birthday < datetime.now()-datetime.now() and contact_birthday - datetime.now() > datetime.now()-datetime.now():

            new_contacts.append(contact)
    return new_contacts


def find_contact(user_id, word):
    contacts = get_contacts_user(user_id=user_id)
    return similar(word, contacts)


def equation(word1, word2):
    s = difflib.SequenceMatcher(None, word1, word2)
    a = s.ratio()
    return a


def similar(word, contacts):
    final_contacts = {}
    arr = contacts

    for i in arr:
        if i.birthday == '':
            try:
                datetime.strptime(word, "%d.%m.%Y")
                continue
            except:
                pass
        final_contacts[i] = equation(i.first_name, word)
        a = equation(i.last_name, word)
        if final_contacts[i] < a:
            final_contacts[i] = a
        a = equation(i.birthday, word)
        if final_contacts[i] < a:
            final_contacts[i] = a
        emails = db.session.query(models.Email).where(
            models.Email.contact_id == i.id).all()
        for email in emails:
            a = equation(email.email, word)
            if final_contacts[i] < a:
                final_contacts[i] = a
        phones = db.session.query(models.Phone).where(
            models.Phone.contact_id == i.id).all()
        for phone in phones:
            a = equation(phone.phone, word)
            if final_contacts[i] < a:
                final_contacts[i] = a
        addresses = db.session.query(models.Address).where(
            models.Address.contact_id == i.id).all()
        for address in addresses:
            a = equation(address.address, word)
            if final_contacts[i] < a:
                final_contacts[i] = a

    sorted_final_contacts = sorted(final_contacts.values(), reverse=True)
    new_sorted_dict = {}
    for i in sorted_final_contacts:

        for k in final_contacts.keys():

            if final_contacts[k] == i:
                new_sorted_dict[k] = final_contacts.pop(k)

                break
    result = []
    full_match_result = []
    average = 0
    for k, v in new_sorted_dict.items():
        average += v
    average = average/len(new_sorted_dict)
    for k, v in new_sorted_dict.items():
        if v >= average:
            result.append(k)
    for k, v in new_sorted_dict.items():
        if v == 1:
            full_match_result.append(k)
    if full_match_result:
        return full_match_result
    return result

def email_delete(email_id):
    db.session.query(models.Email).filter(
        models.Email.id == int(email_id)).delete()
    db.session.commit()


def phone_delete(phone_id):
    db.session.query(models.Phone).filter(
        models.Phone.id == int(phone_id)).delete()
    db.session.commit()


def address_delete(address_id):
    db.session.query(models.Address).filter(
        models.Address.id == int(address_id)).delete()
    db.session.commit()


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
