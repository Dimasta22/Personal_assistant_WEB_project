from src import db
from src import models
import bcrypt


def add_note(new_note, d_escription, t_ags, d_one, u_id):
    add_new_note = models.Note(name=new_note, description=d_escription, tags=t_ags, done=d_one, user_id=u_id)
    db.session.add(add_new_note)
    db.session.commit()
    return


def all_notes(u_id):
    return models.Note.query.filter(models.Note.user_id == u_id).all()


def delete_note(_id):
    db.session.query(models.Note).filter(models.Note.id == _id).delete()
    db.session.commit()


def get_detail(_id):
    note_detail = db.session.query(models.Note).filter(models.Note.id == _id).first()
    return note_detail


def edit_note(_id, new_name_note, new_desc_note, new_tags_note, new_type_note):
    edited_note = db.session.query(models.Note).filter(models.Note.id == _id).first()
    edited_note.name = new_name_note
    edited_note.description = new_desc_note
    edited_note.tags = new_tags_note
    edited_note.done = new_type_note
    db.session.commit()
    return edited_note
