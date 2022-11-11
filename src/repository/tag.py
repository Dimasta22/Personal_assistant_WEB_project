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

def edit_tag():
    pass


def all_tags(u_id):
    return models.Tag.query.filter(models.Tag.user_id == u_id).all()
