import pathlib
from .libs.normalize import normalize

from flask import render_template, request, flash, redirect, url_for, session, make_response, send_file
from werkzeug.utils import secure_filename
from src import db
from . import app
from .libs.file_service import move_user_file
from .libs.validation_file import allowed_file

from .models import FileType, File
from src.repository.files import delete_file


from src.repository import user, contact, tag, note, files

from src.libs.validation_contact import contact_validation
from sqlalchemy.engine import Engine
from sqlalchemy import event
from src.scrappy_libs import currency, football, politics, weather


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


@app.route('/healthcheck', strict_slashes=False)
def healthcheck():
    return 'I am working'


@app.route('/', strict_slashes=False)
def index():
    return render_template('login.html')


@app.route('/registration', methods=['GET', 'POST'], strict_slashes=False)
def registration():
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
    auth = True if 'user_id' in session else False
    if not auth:
        return redirect(url_for('login'))
    session.pop('user_id')
    response = make_response(redirect(url_for('login')))
    return response


@app.route('/account_window', methods=['GET', 'POST'], strict_slashes=False)
def account_window():
    auth = True if 'user_id' in session else False
    if not auth:
        return redirect(url_for('login'))

    if request.method == 'POST':
        city = request.form.get('select_city')
        nick = user.get_user(session['user_id']['id']).nick
        politics_news = politics.parse_finance(10)
        football_news = football.parse_football(10)
        weather_news = weather.parse_weather(city)
        currency_news = currency.parse_currency()
        return render_template('account_window.html',
                               nick=nick,
                               politics_news=politics_news,
                               football_news=football_news,
                               weather_news=weather_news,
                               currency_news=currency_news,
                               city=city)

    nick = user.get_user(session['user_id']['id']).nick
    politics_news = politics.parse_finance(10)
    football_news = football.parse_football(10)
    city = 'Киев'
    weather_news = weather.parse_weather(city)
    currency_news = currency.parse_currency()
    return render_template('account_window.html',
                           nick=nick,
                           politics_news=politics_news,
                           football_news=football_news,
                           weather_news=weather_news,
                           currency_news=currency_news,
                           city=city)


@app.route('/file_uploader', methods=['GET'], strict_slashes=False)
def file_uploader():
    auth = True if 'user_id' in session else False
    if not auth:
        return redirect(url_for('login'))
    user_id = user.get_user(session['user_id']['id']).id
    type_ex = db.session.query(FileType).filter(FileType.files.any(user_id=user_id))
    #type_ex = db.session.query(File).filter(File.user_id == user_id)
    group_is_set = False
    return render_template('file_uploader.html', title='Jarvise\'s File Uploader', types=type_ex,
                           group_is_set=group_is_set)


@app.route('/file_uploader/<group>', methods=['GET'], strict_slashes=False)
def file_uploader_set_files(group):
    auth = True if 'user_id' in session else False
    if not auth:
        return redirect(url_for('login'))
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
        return redirect(url_for('login'))
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
            files.upload_file_for_user(
                session['user_id']['id'], file_path, description)
            flash('Uploaded successfully!')
        else:
            flash('Wrong type of file!')
            return redirect(url_for('file_uploader'))
    return redirect(url_for('file_uploader'))


@app.route('/file_uploader/download/<file_id>', methods=['GET', 'POST'], strict_slashes=False)
def file_download(file_id):
    auth = True if 'user_id' in session else False
    if not auth:
        return redirect(url_for('login'))
    user_id = user.get_user(session['user_id']['id']).id
    file = db.session.query(File).filter(File.id == file_id, File.user_id == user_id).first()
    name = file.path.replace(f'/static/{user_id}/', '\\')
    file_path = pathlib.Path(app.config['DOWNLOAD_FOLDER']) / str(user_id)
    full_path = str(file_path) + name
    return send_file(full_path, download_name=name)


@app.route('/file_uploader/<group>/delete/<file_id>', methods=['GET'], strict_slashes=False)
def delete(group, file_id):
    auth = True if 'user_id' in session else False
    if not auth:
        return redirect(url_for('login'))
    delete_file(file_id, session['user_id']['id'])
    flash('Deletion successfully!')
    return redirect(url_for('file_uploader_set_files', group=group))


@app.route('/Notebook', strict_slashes=False)
def notebook():
    auth = True if 'user_id' in session else False
    if not auth:
        return redirect(url_for('login'))
    nick = user.get_user(session['user_id']['id'])
    all_tags_n = len(tag.all_tags(nick.id))
    all_tags = tag.all_tags(nick.id)
    all_notes = note.all_notes(nick.id)
    all_notes_n = len(note.all_notes(nick.id))
    return render_template('notebook.html', nick=nick.nick, all_tags_num=all_tags_n, all_tags=all_tags,
                           all_notes=all_notes,
                           all_notes_n=all_notes_n)


@app.route('/tags', methods=['GET', 'POST'], strict_slashes=False)
def tags():
    auth = True if 'user_id' in session else False
    if not auth:
        return redirect(url_for('login'))
    nick = user.get_user(session['user_id']['id'])
    if request.method == "POST":
        tag_name = request.form.get("tag_name")
        if tag.search_tags_user(tag_name, nick.id) is None:
            flash('All good')
            tag.add_tag(tag_name, nick.id)
            return render_template('tags.html', nick=nick.nick, message='All good')
        else:
            flash('Tag name already exists')
            return render_template('tags.html', nick=nick.nick, message='Tag name already exists')
    return render_template('tags.html', nick=nick.nick)


@app.route("/delete_tag/<_id>", strict_slashes=False)
def delete_tag(_id):
    auth = True if 'user_id' in session else False
    if not auth:
        return redirect(url_for('login'))
    tag.delete_tag(_id)
    return redirect("/Notebook")


@app.route('/detail_tag/<_id>', strict_slashes=False)
def detail_tag(_id):
    auth = True if 'user_id' in session else False
    if not auth:
        return redirect(url_for('login'))
    nick = user.get_user(session['user_id']['id'])
    d_tag = tag.get_detail(_id)
    return render_template('tag_detail.html', nick=nick.nick, d_tag=d_tag)


@app.route('/edit_tag/<_id>', methods=['GET', 'POST'], strict_slashes=False)
def edit_tag(_id):
    auth = True if 'user_id' in session else False
    if not auth:
        return redirect(url_for('login'))
    nick = user.get_user(session['user_id']['id'])
    d_tag = tag.get_detail(_id)
    if request.method == "POST":
        d_tag = tag.get_detail(_id)
        tag_new = request.form.get("tag_name")
        if tag.search_tags(tag_new) is None:
            # flash('Tag was edited')
            tag.edit_tag(d_tag.id, tag_new)
            return redirect("/Notebook")
            # return render_template('tag_edit.html', nick=nick.nick, d_tag=d_tag, message='Tag was edited')
        elif tag_new == tag.search_tags(tag_new).name:
            flash('This name already exist')
            return render_template('tag_edit.html', d_tag=d_tag, nick=nick.nick, message='This name already exist')
    return render_template('tag_edit.html', d_tag=d_tag, nick=nick.nick)


@app.route('/notes', methods=['GET', 'POST'], strict_slashes=False)
def notes():
    auth = True if 'user_id' in session else False
    if not auth:
        return redirect(url_for('login'))
    nick = user.get_user(session['user_id']['id'])
    all_tags = tag.all_tags(nick.id)
    if request.method == "POST":
        flash('This name already exist')
        # flash('Note was added')
        note_n = request.form.get("note_name")
        note_des = request.form.get("note_description")
        note_tgs = request.form.getlist("tags")
        tags_in_form = tag.add_to_notes(note_tgs)
        note_ty = request.form.get("note_type")
        note_ty = (False if note_ty == '0' else True)
        if note.search_note_name(note_n, nick.id) is None:
            note.add_note(note_n, note_des, tags_in_form, note_ty, nick.id)
            return render_template('notes.html', nick=nick.nick, all_tags=all_tags, message='Note was added')
        else:
            # flash('This name already exist')
            return render_template('notes.html', nick=nick.nick, all_tags=all_tags, message='This name already exist')
    return render_template('notes.html', nick=nick.nick, all_tags=all_tags, message='Note was added')


@app.route("/delete_note/<_id>", strict_slashes=False)
def delete_note(_id):
    auth = True if 'user_id' in session else False
    if not auth:
        return redirect(url_for('login'))
    note.delete_note(_id)
    return redirect("/Notebook")


@app.route('/detail_note/<_id>', strict_slashes=False)
def detail_note(_id):
    auth = True if 'user_id' in session else False
    if not auth:
        return redirect(url_for('login'))
    nick = user.get_user(session['user_id']['id'])
    d_note = note.get_detail(_id)
    tags_n = note.note_tags_to_string(d_note.tags)
    return render_template('note_detail.html', nick=nick.nick, d_note=d_note, tags_n=tags_n)


@app.route('/edit_note/<_id>', methods=['GET', 'POST'], strict_slashes=False)
def edit_note(_id):
    auth = True if 'user_id' in session else False
    if not auth:
        return redirect(url_for('login'))
    nick = user.get_user(session['user_id']['id'])
    all_tags = tag.all_tags(nick.id)
    d_note = note.get_detail(_id)
    if request.method == "POST":
        flash('This name already exist')
        d_note = note.get_detail(_id)
        note_n = request.form.get("note_name")
        note_des = request.form.get("note_description")
        note_tgs = request.form.getlist("tags")
        tags_in_form = tag.add_to_notes(note_tgs)
        note_ty = request.form.get("note_type")
        note_ty = (False if note_ty == '0' else True)
        if note.search_note_name(note_n, nick.id) is None:
            note.edit_note(d_note.id, note_n, note_des, tags_in_form, note_ty)
            return redirect("/Notebook")
        else:
            return render_template('note_edit.html', nick=nick.nick, all_tags=all_tags, d_note=d_note,
                                   message='This name already exist')
    return render_template('note_edit.html', nick=nick.nick, all_tags=all_tags, d_note=d_note)


@app.route('/search_notes_tags', strict_slashes=False)
def search_note_tag():
    auth = True if 'user_id' in session else False
    if not auth:
        return redirect(url_for('login'))
    nick = user.get_user(session['user_id']['id'])
    all_tags = tag.all_tags(nick.id)
    return render_template('search_n.html', nick=nick.nick, all_tags=all_tags)


@app.route('/search_all_done_notes', strict_slashes=False)
def search_note_done():
    auth = True if 'user_id' in session else False
    if not auth:
        return redirect(url_for('login'))
    nick = user.get_user(session['user_id']['id'])
    done_notes = note.search_all_notes(nick.id, 1)
    d_s_tags = note.note_tags_to_string(done_notes)
    return render_template('search_notes_tags_result.html', nick=nick.nick, done_notes=done_notes, d_s_tags=d_s_tags)


@app.route('/search_all_undone_notes', strict_slashes=False)
def search_note_undone():
    auth = True if 'user_id' in session else False
    if not auth:
        return redirect(url_for('login'))
    nick = user.get_user(session['user_id']['id'])
    undone_notes = note.search_all_notes(nick.id, 0)
    u_s_tags = note.note_tags_to_string(undone_notes)
    return render_template('search_notes_tags_result.html', nick=nick.nick, undone_notes=undone_notes,
                           u_s_tags=u_s_tags)


@app.route('/search_by_phrase', methods=['GET', 'POST'], strict_slashes=False)
def search_by_phrases():
    auth = True if 'user_id' in session else False
    if not auth:
        return redirect(url_for('login'))
    nick = user.get_user(session['user_id']['id'])
    if request.method == "POST":
        phrase = request.form.get('note_phrase')
        note_tgs = request.form.getlist("tags")
        if not phrase and not note_tgs:
            flash('Nothing to show')
            return render_template('search_notes_tags_result.html', nick=nick.nick, message='Nothing to show')
        if phrase and not note_tgs:
            flash('No Tags included')
            result_note = note.all_find_notes(nick.id, phrase)
            result_notes = note.result_notes_into_list(result_note)
            return render_template('search_notes_tags_result.html', nick=nick.nick, result=result_note, phrase=phrase,
                                   result_notes=result_notes, message='No Tags included')
        if not phrase and note_tgs:
            flash('No Notes included')
            result_tag = tag.all_find_tags(nick.id, note_tgs)
            result_note_tags = note.result_notes_into_list(result_tag)
            note_tgs = ", ".join(note_tgs)
            return render_template('search_notes_tags_result.html', nick=nick.nick, result_tag=result_tag,
                                   result_note_tags=result_note_tags, note_tgs=note_tgs, message='No Tags included')
        if phrase and note_tgs:
            flash('All included')
            result_note = note.all_find_notes(nick.id, phrase)
            result_notes = note.result_notes_into_list(result_note)
            result_tag = tag.all_find_tags(nick.id, note_tgs)
            result_note_tags = note.result_notes_into_list(result_tag)
            all_in = 1
            note_tgs = ", ".join(note_tgs)
            return render_template('search_notes_tags_result.html', nick=nick.nick, result_tag=result_tag,
                                   all_in=all_in, phrase=phrase,
                                   result_all=result_note, result_notes_all=result_notes,
                                   result_note_tags=result_note_tags, note_tgs=note_tgs, message='All included')
    return render_template('search_notes_tags_result.html', nick=nick.nick)

@app.route('/contacts', methods=['GET', 'POST'], strict_slashes=False)
def contacts():
    auth = True if 'user_id' in session else False
    if not auth:
        return redirect(url_for('login'))
    nick = user.get_user(session['user_id']['id']).nick
    contacts = contact.get_contacts_user(session['user_id']['id'])
    return render_template('/contacts.html', contacts=contacts, nick=nick, href_='contact',
                           amount_contacts=len(contacts))


@app.route('/add_contact', methods=['GET', 'POST'], strict_slashes=False)
def add_contact():
    auth = True if 'user_id' in session else False
    if not auth:
        return redirect(url_for('login'))
    nick = user.get_user(session['user_id']['id']).nick
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        birthday = request.form.get('birthday')
        email = request.form.get('email')
        address = request.form.get('address')
        cell_phone = request.form.get('cell_phone')
        validation = contact_validation(first_name=first_name,
                                        last_name=last_name,
                                        birthday=birthday,
                                        email=email,
                                        address=address,
                                        phone=cell_phone)
        if validation is not None:
            flash(validation)
            return redirect(request.url)

        contact.create_contact(first_name, last_name, birthday,
                               email, address, cell_phone, session['user_id']['id'])
    return render_template('add_contact.html', nick=nick)


@app.route('/show_contact_birthday', methods=['GET', 'POST'], strict_slashes=False)
def show_contact_birthday():
    auth = True if 'user_id' in session else False
    if not auth:
        return redirect(url_for('login'))
    nick = user.get_user(session['user_id']['id']).nick
    contacts = contact.get_contacts_user(session['user_id']['id'])
    birthday_date = 'dd/mm/yyyy'
    if request.method == 'POST':
        birthday_date = request.form.get('calendar')
        print(birthday_date)
        if birthday_date == '':
            flash('Choose date!')
            return redirect(request.url)
        contacts = contact.find_contact_birthday(
            session['user_id']['id'], birthday_date)
    return render_template('/contacts.html', contacts=contacts, nick=nick, href_='contact',
                           amount_contacts=len(contacts), calendar=birthday_date)


@app.route('/find_contact', methods=['GET', 'POST'], strict_slashes=False)
def find_contact():
    auth = True if 'user_id' in session else False
    if not auth:
        return redirect(url_for('login'))
    nick = user.get_user(session['user_id']['id']).nick
    contacts = contact.get_contacts_user(session['user_id']['id'])
    if request.method == 'POST':
        word = request.form.get('find')
        print(word)
        contacts = contact.find_contact(session['user_id']['id'], word)
    return render_template('/contacts.html', contacts=contacts, nick=nick, href_='contact',
                           amount_contacts=len(contacts))


@app.route('/delete_contact/<contact_id>', methods=["POST"], strict_slashes=False)
def contact_delete(contact_id):
    auth = True if 'user_id' in session else False
    if not auth:
        return redirect(url_for('login'))
    if request.method == 'POST':
        contact.cont_delete(contact_id, session['user_id']['id'])
        flash('Operation successfully!')
    return redirect(url_for('contacts'))


@app.route('/add_email/<contact_id>', methods=["POST"], strict_slashes=False)
def add_email(contact_id):
    auth = True if 'user_id' in session else False
    if not auth:
        return redirect(url_for('login'))
    contact_ = contact.get_contacts_user_by_id(
        session['user_id']['id'], contact_id)
    if request.method == 'POST':
        if request.form.get('email') is not None:
            email = request.form.get('email')
            validation = contact_validation(email=email)
            if validation is not None:
                flash(validation[:-1])
                return render_template('add_email.html', contact=contact_)
            contact.add_email(contact_id, email)
    return render_template('add_email.html', contact=contact_)


@app.route('/add_address/<contact_id>', methods=["POST"], strict_slashes=False)
def add_address(contact_id):
    auth = True if 'user_id' in session else False
    if not auth:
        return redirect(url_for('login'))
    contact_ = contact.get_contacts_user_by_id(
        session['user_id']['id'], contact_id)
    if request.method == 'POST':
        address = request.form.get('address')
        if request.form.get('address') is not None:
            contact.add_address(contact_id, address)
    return render_template('add_address.html', contact=contact_)


@app.route('/add_phone/<contact_id>', methods=["POST"], strict_slashes=False)
def add_phone(contact_id):
    auth = True if 'user_id' in session else False
    if not auth:
        return redirect(url_for('login'))
    contact_ = contact.get_contacts_user_by_id(
        session['user_id']['id'], contact_id)
    if request.method == 'POST':
        phone = request.form.get('phone')
        if request.form.get('phone') is not None:
            validation = contact_validation(phone=phone)
            if validation is not None:
                flash(validation[:-1])
                return render_template('add_phone.html', contact=contact_)
            contact.add_phone(contact_id, phone)
    return render_template('add_phone.html', contact=contact_)


@app.route('/edit_contact/<contact_id>', methods=["POST"], strict_slashes=False)
def edit_contact(contact_id):
    auth = True if 'user_id' in session else False
    if not auth:
        return redirect(url_for('login'))
    nick = user.get_user(session['user_id']['id']).nick
    contact_ = contact.get_contacts_user_by_id(
        session['user_id']['id'], contact_id)
    if request.method == 'POST':
        pass
    return render_template('edit_contact.html', contact_id=contact_id, nick=nick, contact=contact_)


@app.route('/edit_name/<contact_id>', methods=['GET', 'POST'], strict_slashes=False)
def edit_name(contact_id):
    auth = True if 'user_id' in session else False
    if not auth:
        return redirect(url_for('login'))
    contact_ = contact.get_contacts_user_by_id(
        session['user_id']['id'], contact_id)
    if request.method == 'POST':
        if request.form.get('name') is not None:
            name = request.form.get('name')
            contact.update_first_name(
                contact_id, session['user_id']['id'], name)
    return render_template('edit_name.html', contact=contact_, first_name_obj=contact_.first_name)


@app.route('/edit_last_name/<contact_id>', methods=['GET', 'POST'], strict_slashes=False)
def edit_last_name(contact_id):
    auth = True if 'user_id' in session else False
    if not auth:
        return redirect(url_for('login'))
    contact_ = contact.get_contacts_user_by_id(
        session['user_id']['id'], contact_id)
    if request.method == 'POST':
        if request.form.get('last_name') is not None:
            last_name = request.form.get('last_name')
            contact.update_last_name(
                contact_id, session['user_id']['id'], last_name)
    return render_template('edit_last_name.html', contact=contact_, last_name_obj=contact_.last_name)


@app.route('/edit_birthday/<contact_id>', methods=['GET', 'POST'], strict_slashes=False)
def edit_birthday(contact_id):
    auth = True if 'user_id' in session else False
    if not auth:
        return redirect(url_for('login'))
    contact_ = contact.get_contacts_user_by_id(
        session['user_id']['id'], contact_id)
    if request.method == 'POST':
        if request.form.get('birthday') is not None:
            birthday = request.form.get('birthday')
            validation = contact_validation(birthday=birthday)
            if validation is not None:
                flash(validation[:-1])
                return render_template('edit_birthday.html', contact=contact_, birthday_obj=contact_.birthday)
            contact.update_birthday(
                contact_id, session['user_id']['id'], birthday)
    return render_template('edit_birthday.html', contact=contact_, birthday_obj=contact_.birthday)


@app.route('/edit_email/<contact_id>/<email_id>', methods=['GET', 'POST'], strict_slashes=False)
def edit_email(contact_id, email_id):
    auth = True if 'user_id' in session else False
    if not auth:
        return redirect(url_for('login'))
    contact_ = contact.get_contacts_user_by_id(
        session['user_id']['id'], contact_id)
    if request.method == 'POST':
        if request.form.get('email') is not None:
            email = request.form.get('email')
            validation = contact_validation(email=email)
            if validation is not None:
                flash(validation[:-1])
                return render_template('edit_email.html', contact=contact_,
                                       email=email_id,
                                       email_obj=contact.get_email(contact_id=contact_id, email_id=email_id)[0])
            contact.update_email(contact_id, email_id, email)
    return render_template('edit_email.html', contact=contact_, email=email_id,
                           email_obj=contact.get_email(contact_id=contact_id, email_id=email_id)[0])


@app.route('/edit_phone/<contact_id>/<phone_id>', methods=['GET', 'POST'], strict_slashes=False)
def edit_phone(contact_id, phone_id):
    auth = True if 'user_id' in session else False
    if not auth:
        return redirect(url_for('login'))
    contact_ = contact.get_contacts_user_by_id(
        session['user_id']['id'], contact_id)
    if request.method == 'POST':
        if request.form.get('phone') is not None:
            phone = request.form.get('phone')
            validation = contact_validation(phone=phone)
            if validation is not None:
                flash(validation[:-1])
                return render_template('edit_phone.html', contact=contact_, phone=phone_id,
                                       phone_obj=contact.get_phone(contact_id=contact_id, phone_id=phone_id)[0])
            contact.update_phone(contact_id, phone_id, phone)
    return render_template('edit_phone.html', contact=contact_, phone=phone_id,
                           phone_obj=contact.get_phone(contact_id=contact_id, phone_id=phone_id)[0])


@app.route('/edit_address/<contact_id>/<address_id>', methods=['GET', 'POST'], strict_slashes=False)
def edit_address(contact_id, address_id):
    auth = True if 'user_id' in session else False
    if not auth:
        return redirect(url_for('login'))
    contact_ = contact.get_contacts_user_by_id(
        session['user_id']['id'], contact_id)
    if request.method == 'POST':
        if request.form.get('address') is not None:
            address = request.form.get('address')
            contact.update_address(contact_id, address_id, address)
    return render_template('edit_address.html', contact=contact_, address=address_id,
                           address_obj=contact.get_address(contact_id=contact_id, address_id=address_id)[0])


