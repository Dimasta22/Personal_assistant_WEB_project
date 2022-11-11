from src import db
from src import models
import bcrypt


def add_tag(new_tag):
    add_new_tag = models.Tag(name=new_tag)
    db.session.add(add_new_tag)
    db.session.commit()
    return


def delete_tag(_id):
    db.session.query(models.Tag).filter(models.Tag.id == _id).delete()
    db.session.commit()


def get_detail(_id):
    tag_detail = db.session.query(models.Tag).filter(models.Tag.id == _id).first()
    return tag_detail

def edit_tag():
    pass


def all_tags():
    return models.Tag.query.all()
