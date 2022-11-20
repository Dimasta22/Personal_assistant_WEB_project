import pathlib
from src.models import FileType, File
from sqlalchemy import and_
from src import db
from src import models
from src.libs.file_service import move_user_file, delete_user_file


def get_type(extention):
    types = {'Audio': ['.wav', '.ogg', '.flac', '.m4a', '.mp3'], 'Video': ['.mp4', '.3gp', '.avi', '.mkv'],
             'Documents': ['.txt', '.doc', '.docx', '.pdf', ], 'Images': ['.png', '.jpg', '.jpeg', '.gif']}
    for g, t in types.items():
        if extention in t:
            return g
    return 'Other'


def get_pictures_user(user_id):
    return db.session.query(models.File).filter(models.File.user_id == user_id).all()


def get_file_user(pic_id, user_id):
    return db.session.query(models.File).filter(
        and_(models.File.user_id == user_id, models.File.id == pic_id)).one()


def upload_file_for_user(user_id, file_path, description):
    filename, size = move_user_file(user_id, file_path)
    extension = pathlib.Path(filename).suffix
    file_type = db.session.query(FileType).filter(FileType.name == get_type(extension)).first()
    file = models.File(description=description, user_id=user_id, path=filename, size=size, file_type=file_type)
    db.session.add(file)
    db.session.commit()


def delete_file(file_id, user_id):
    file = get_file_user(file_id, user_id)
    db.session.query(File).filter(
        and_(File.user_id == user_id, File.id == file_id)).delete()
    delete_user_file(file.path)
    db.session.commit()
