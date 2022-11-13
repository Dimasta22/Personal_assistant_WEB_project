from src import db
from src import models
import bcrypt


def add_tag(new_tag, u_id):
    add_new_tag = models.Tag(name=new_tag, user_id=u_id)
    db.session.add(add_new_tag)
    db.session.commit()
    return


def delete_tag(_id):
    db.session.query(models.Tag).filter(models.Tag.id == _id).delete()
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

