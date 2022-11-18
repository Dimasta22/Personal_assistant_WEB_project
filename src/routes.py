import pathlib
from .libs.normalize import normalize
from flask import render_template, request, flash, redirect, url_for, session, make_response, send_file
from werkzeug.utils import secure_filename
from src import db
from . import app
from src.repository import user, files
from .libs.validation_file import allowed_file
from .models import FileType, File
from src.repository.files import delete_file


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
    type_ex = db.session.query(FileType).filter(FileType.files.any(user_id=user_id))
    group_is_set = False
    return render_template('file_uploader.html', title='Jarvise\'s File Uploader', types=type_ex,
                           group_is_set=group_is_set)


@app.route('/file_uploader/<group>', methods=['GET'], strict_slashes=False)
def file_uploader_set_files(group):
    user_id = user.get_user(session['user_id']['id']).id
    type_ex = db.session.query(FileType).filter(FileType.files.any(user_id=user_id)).all()
    groups = ['Audio', 'Video', 'Documents', 'Images', 'Other']
    group_is_set = False
    page = request.args.get('page')
    if page and page.isdigit():
        page = int(page)
    else:
        page = 1
    if group in groups:
        group_is_set = True
        chosen_group = db.session.query(FileType).filter(FileType.name == group).first()
        selected_files = db.session.query(File).filter(File.user_id == user_id, File.type_id == chosen_group.id)
        selected_files = selected_files.paginate(page=page, per_page=3)
        return render_template('file_uploader.html', title='Jarvise\'s File Uploader', types=type_ex,
                               group_is_set=group_is_set, selected_files=selected_files, group=group)
    return render_template('file_uploader.html', title='Jarvise\'s File Uploader', types=type_ex,
                           group_is_set=group_is_set, group=group)


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


@app.route('/file_uploader/download/<file_id>', methods=['GET', 'POST'], strict_slashes=False)
def file_download(file_id):
    user_id = user.get_user(session['user_id']['id']).id
    file = db.session.query(File).filter(File.id == file_id, File.user_id == user_id).first()
    name = file.path.replace(f'/static/{user_id}/', '\\')
    file_path = pathlib.Path(app.config['DOWNLOAD_FOLDER']) / str(user_id)
    full_path = str(file_path) + name
    return send_file(full_path, download_name=name)


@app.route('/file_uploader/<group>/delete/<file_id>', methods=['GET'], strict_slashes=False)
def delete(group, file_id):
    delete_file(file_id, session['user_id']['id'])
    flash('Deletion successfully!')
    return redirect(url_for('file_uploader_set_files', group=group))


