from src import db
from src import models
import bcrypt


def add_note(new_note, d_escription, t_ags, d_one, u_id):
    add_new_note = models.Note(name=new_note, description=d_escription, tags=t_ags, done=d_one, user_id=u_id)
    db.session.add(add_new_note)
    db.session.commit()
    return
