from src import db
from src import models
from sqlalchemy import and_, func
import bcrypt


def add_tag(new_tag, u_id):
    add_new_tag = models.Tag(name=new_tag, user_id=u_id)
    db.session.add(add_new_tag)
    db.session.commit()
    return


def delete_tag(_id):
    tag = db.session.query(models.Tag).get(_id)
    if tag:
        db.session.delete(tag)
        db.session.commit()


def get_detail(_id):
    tag_detail = db.session.query(models.Tag).filter(models.Tag.id == _id).first()
    return tag_detail


def edit_tag(_id, new_name_tag):
    edited_tag = db.session.query(models.Tag).filter(models.Tag.id == _id).first()
    edited_tag.name = new_name_tag
    db.session.commit()
    # return edited_tag


def all_tags(u_id):
    return models.Tag.query.filter(models.Tag.user_id == u_id).all()


def add_to_notes(many_tags):
    multi_tags = []
    for tag in many_tags:
        multi_tags.append(db.session.query(models.Tag).filter(models.Tag.name == tag).first())
    return multi_tags


def search_tags(search_name_tag):
    search_tag = db.session.query(models.Tag).filter(models.Tag.name == search_name_tag).first()
    return search_tag


def search_tags_user(search_name_tag, u_id):
    search_tag_u = db.session.query(models.Tag).filter(
        and_(models.Tag.name == search_name_tag, models.Tag.user_id == u_id)).first()
    return search_tag_u


def convert_to_tag_from_list(list_tags_names):
    tags_list = []
    for tag in list_tags_names:
        tg = db.session.query(models.Tag).filter(models.Tag.name == tag).first()
        if tg in tags_list:
            continue
        tags_list.append(tg)
    return tags_list


def all_find_tags(u_id, note_tgs):
    all_tags_search_result = []
    c_tags = convert_to_tag_from_list(note_tgs)
    all_n = models.Note.query.filter(models.Note.user_id == u_id).all()
    for note in all_n:
        if note.tags == c_tags:
            all_tags_search_result.append(note)
    return all_tags_search_result
