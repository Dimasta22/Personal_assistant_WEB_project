from src import db
from src import models
import bcrypt


def add_tag(new_tag):
    add_new_tag = models.Tag(name=new_tag)
    db.session.add(add_new_tag)
    db.session.commit()
    return


def delete_tag():
    pass


def edit_tag():
    pass


def all_tags():
    return len(models.Tag.query.all())
