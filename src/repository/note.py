from src import db
from src import models
from sqlalchemy import and_, func, or_
import bcrypt


def add_note(new_note, d_escription, t_ags, d_one, u_id):
    add_new_note = models.Note(name=new_note, description=d_escription, tags=t_ags, done=d_one, user_id=u_id)
    db.session.add(add_new_note)
    db.session.commit()
    return


def all_notes(u_id):
    return models.Note.query.filter(models.Note.user_id == u_id).all()


def delete_note(_id):
    note = db.session.query(models.Note).get(_id)
    print(note)
    if note:
        db.session.delete(note)
        db.session.commit()


def get_detail(_id):
    note_detail = db.session.query(models.Note).filter(models.Note.id == _id).first()
    return note_detail


def edit_note(_id, new_name_note, new_desc_note, new_tags_note, new_type_note):
    edited_note = db.session.query(models.Note).filter(models.Note.id == _id).first()
    if not new_name_note == '':
        edited_note.name = new_name_note
    if not new_desc_note == '':
        edited_note.description = new_desc_note
    if not new_tags_note == '':
        edited_note.tags = new_tags_note
    if not new_type_note == '':
        edited_note.done = new_type_note
    db.session.commit()
    return edited_note


def search_all_notes(u_id, note_type):
    search_result = db.session.query(models.Note).filter(
        and_(models.Note.done == note_type, models.Note.user_id == u_id)).all()
    return search_result


def all_find_notes(u_id, what_to_find):
    string_to_find = "%{}%".format(what_to_find)
    s1 = db.session.query(models.Note).filter(
        and_(models.Note.name.like(string_to_find), (models.Note.user_id == u_id))).all()
    s2 = db.session.query(models.Note).filter(
        and_(models.Note.description.like(string_to_find), (models.Note.user_id == u_id))).all()
    search = list(set(s1) | set(s2))
    return search


def note_tags_to_string(notes_tags):
    all_tags = ''
    for tag in notes_tags:
        all_tags = all_tags + "!@#" + tag.name
    return all_tags.replace('!@#', ' , ').lstrip(' ,')


def result_notes_into_list(note_list):
    search_note_pool = []
    for i in note_list:
        temp_pool = [i.name, i.description, note_tags_to_string(i.tags)]
        search_note_pool.append(temp_pool)
    return search_note_pool


def search_note_name(new_name, u_id):
    search_tag = db.session.query(models.Note).filter(and_(models.Note.name == new_name),
                                                      (models.Note.user_id == u_id)).first()
    return search_tag
