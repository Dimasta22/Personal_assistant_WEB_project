from src import db
from src import models
import bcrypt


def update_login_for_user(nick, password):
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=10))
    user = models.User(nick=nick, hash=hashed)
    db.session.add(user)
    db.session.commit()
    return user


def checkout_login_for_user(nick, password):
    user = find_by_nick(nick)
    if not user:
        return None
    if not bcrypt.checkpw(password.encode('utf-8'), user.hash):
        return None
    return user


def find_by_nick(nick):
    user = db.session.query(models.User).filter(models.User.nick == nick).first()
    return user


def get_user(user_id):
    user = db.session.query(models.User).filter(models.User.id == user_id).first()
    return user
