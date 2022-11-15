import pathlib
from src.models import FileType
from sqlalchemy import and_, select
from src import db
from src import models
from src.libs.file_service import move_user_file, delete_user_file
from src.repository.user import find_by_nick


def get_type(extention):
    types = {'Audio': ['.wav', '.ogg', '.flac', '.m4a'], 'Video': ['.mp4', '.3gp', '.avi', '.mkv'],
             'Documents': ['.txt', '.doc', '.docx', '.pdf', ], 'Images': ['.png', '.jpg', '.jpeg', '.gif']}
    for g, t in types.items():
        if extention in t:
            return g
    return 'Other'


def get_pictures_user(user_id):
    return db.session.query(models.File).filter(models.File.user_id == user_id).all()


def get_picture_user(pic_id, user_id):
    return db.session.query(models.File).filter(
        and_(models.File.user_id == user_id, models.File.id == pic_id)).one()


def upload_file_for_user(user_id, file_path, description):
    filename, size = move_user_file(user_id, file_path)
    extension = pathlib.Path(filename).suffix
    file_type = db.session.query(FileType).filter(FileType.name == get_type(extension)).first()

    file = models.File(description=description, user_id=user_id, path=filename, size=size, file_type=file_type)
    db.session.add(file)
    db.session.commit()


def update_picture(pic_id, user_id, description):
    picture = get_picture_user(pic_id, user_id)
    picture.description = description
    db.session.commit()


def delete_picture(pic_id, user_id):
    picture = get_picture_user(pic_id, user_id)
    db.session.query(models.Picture).filter(
        and_(models.Picture.user_id == user_id, models.Picture.id == pic_id)).delete()
    delete_user_file(picture.path)
    db.session.commit()
