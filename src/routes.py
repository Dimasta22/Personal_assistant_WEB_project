import pathlib
from .libs.normalize import normalize
import sqlalchemy.exc
from flask import render_template, request, flash, redirect, url_for, session, make_response
from werkzeug.utils import secure_filename
from src import db
from . import app
from src.repository import user, files
from .libs.file_service import move_user_file
from .libs.validation_file import allowed_file
from .models import FileType

@app.route('/healthcheck', strict_slashes=False)
def healthcheck():
    return 'I am working'


@app.route('/', strict_slashes=False)
def index():
    return render_template('login.html')


@app.route('/registration', methods=['GET', 'POST'], strict_slashes=False)
def registration():
    # auth = True if 'username' in session else False
    if request.method == 'POST':
        if request.form.get('login'):
            return redirect(url_for('login'))
        nick = request.form.get('nickname')
        password = request.form.get('password')
        if user.find_by_nick(nick) is None:
            registration_contact = user.update_login_for_user(nick, password)
            return render_template('login.html')
        else:
            flash('User already exist')
            return render_template('registration.html', message='User already exist')
    return render_template('registration.html')


@app.route('/login', methods=['GET', 'POST'], strict_slashes=False)
def login():
    # auth = True if 'username' in session else False
    if request.method == 'POST':
        nick = request.form.get('nickname')
        password = request.form.get('password')
        login_data = user.checkout_login_for_user(nick, password)
        if login_data is None:
            flash('pass')
            return redirect(url_for('login'))
        session['user_id'] = {'id': login_data.id}
        response = make_response(redirect(url_for('account_window')))
        return response
    return render_template('login.html')


@app.route('/logout', strict_slashes=False)
def logout():
    session.pop('user_id')
    response = make_response(redirect(url_for('login')))
    return response


@app.route('/account_window', strict_slashes=False)
def account_window():
    # auth = True if 'username' in session else False
    nick = user.get_user(session['user_id']['id']).nick
    # contacts = contact.get_all_contacts(session['user_id']['id'])
    # contact_notes = notes.get_all_notes(session['user_id']['id'])
    return render_template('account_window.html', nick=nick)


@app.route('/file_uploader', methods=['GET'], strict_slashes=False)
def file_uploader():
    user_id = user.get_user(session['user_id']['id']).id
    #type_ex = db.session.query(File).filter(File.user_id==user_id).all()
    type_ex = db.session.query(FileType).filter(FileType.files.any(user_id=user_id)).all()
    return render_template('file_uploader.html', title='Jarvise\'s File Uploader', types=type_ex)


@app.route('/file_uploader/upload', methods=['GET', 'POST'], strict_slashes=False)
def file_upload():
    auth = True if 'user_id' in session else False
    if not auth:
        return redirect(request.url)
    if request.method == 'POST':
        description = request.form.get('description')
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(normalize(file.filename))
            file_path = pathlib.Path(app.config['UPLOAD_FOLDER']) / filename
            file.save(file_path)
            files.upload_file_for_user(session['user_id']['id'], file_path, description)
            flash('Uploaded successfully!')
        else:
            flash('Wrong type of file!')
            return redirect(url_for('file_uploader'))
    return redirect(url_for('file_uploader'))
