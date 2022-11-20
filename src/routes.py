import pathlib
from .libs.normalize import normalize
from flask import render_template, request, flash, redirect, url_for, session, make_response
from werkzeug.utils import secure_filename
from src import db
from . import app

from .libs.validation_file import allowed_file
from .models import FileType

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


@app.route('/account_window', methods=['GET', 'POST'], strict_slashes=False)
def account_window():
    # auth = True if 'username' in session else False
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
                               currency_news=currency_news)

    nick = user.get_user(session['user_id']['id']).nick
    politics_news = politics.parse_finance(10)
    football_news = football.parse_football(10)
    weather_news = weather.parse_weather('Киев')
    currency_news = currency.parse_currency()
    return render_template('account_window.html',
                           nick=nick,
                           politics_news=politics_news,
                           football_news=football_news,
                           weather_news=weather_news,
                           currency_news=currency_news)


@app.route('/file_uploader', methods=['GET'], strict_slashes=False)
def file_uploader():
    user_id = user.get_user(session['user_id']['id']).id
    # type_ex = db.session.query(File).filter(File.user_id==user_id).all()
    type_ex = db.session.query(FileType).filter(
        FileType.files.any(user_id=user_id)).all()
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
            files.upload_file_for_user(
                session['user_id']['id'], file_path, description)
            flash('Uploaded successfully!')
        else:
            flash('Wrong type of file!')
            return redirect(url_for('file_uploader'))
    return redirect(url_for('file_uploader'))


@app.route('/Notebook', strict_slashes=False)
def notebook():
    nick = user.get_user(session['user_id']['id'])
    all_tags_n = len(tag.all_tags(nick.id))
    all_tags = tag.all_tags(nick.id)
    all_notes = note.all_notes(nick.id)
    all_notes_n = len(note.all_notes(nick.id))
    return render_template('notebook.html',
                           nick=nick,
                           all_tags_num=all_tags_n,
                           all_tags=all_tags,
                           all_notes=all_notes,
                           all_notes_n=all_notes_n)


@app.route('/tags', methods=['GET', 'POST'], strict_slashes=False)
def tags():
    nick = user.get_user(session['user_id']['id'])
    if request.method == "POST":
        tag_name = request.form.get("tag_name")
        tag.add_tag(tag_name, nick.id)
    return render_template('tags.html', nick=nick)


@app.route("/delete_tag/<_id>", strict_slashes=False)
def delete_tag(_id):
    tag.delete_tag(_id)
    return redirect("/Notebook")


@app.route('/detail_tag/<_id>', strict_slashes=False)
def detail_tag(_id):
    d_tag = tag.get_detail(_id)
    return render_template('tag_detail.html', d_tag=d_tag)


@app.route('/edit_tag/<_id>', methods=['GET', 'POST'], strict_slashes=False)
def edit_tag(_id):
    nick = user.get_user(session['user_id']['id'])
    d_tag = tag.get_detail(_id)
    if request.method == "POST":
        d_tag = tag.get_detail(_id)
        tag_new = request.form.get("tag_name")
        tag.edit_tag(d_tag.id, tag_new)
    return render_template('tag_edit.html', d_tag=d_tag)


@app.route('/notes', methods=['GET', 'POST'], strict_slashes=False)
def notes():
    nick = user.get_user(session['user_id']['id'])
    all_tags = tag.all_tags(nick.id)
    if request.method == "POST":
        note_n = request.form.get("note_name")
        note_des = request.form.get("note_description")
        note_tgs = request.form.getlist("tags")
        tags_in_form = tag.add_to_notes(note_tgs)
        note_ty = request.form.get("note_type")
        note_ty = (False if note_ty == '0' else True)
        note.add_note(note_n, note_des, tags_in_form, note_ty, nick.id)
    return render_template('notes.html', nick=nick, all_tags=all_tags)


@app.route("/delete_note/<_id>", strict_slashes=False)
def delete_note(_id):
    note.delete_note(_id)
    return redirect("/Notebook")


@app.route('/detail_note/<_id>', strict_slashes=False)
def detail_note(_id):
    d_note = note.get_detail(_id)
    return render_template('note_detail.html', d_note=d_note)


@app.route('/edit_note/<_id>', methods=['GET', 'POST'], strict_slashes=False)
def edit_note(_id):
    nick = user.get_user(session['user_id']['id'])
    all_tags = tag.all_tags(nick.id)
    d_note = note.get_detail(_id)
    if request.method == "POST":
        d_note = note.get_detail(_id)
        note_n = request.form.get("note_name")
        note_des = request.form.get("note_description")
        note_tgs = request.form.getlist("tags")
        tags_in_form = tag.add_to_notes(note_tgs)
        note_ty = request.form.get("note_type")
        note_ty = (False if note_ty == '0' else True)
        note.edit_note(d_note.id, note_n, note_des, tags_in_form, note_ty)
    return render_template('note_edit.html', all_tags=all_tags, d_note=d_note)


@app.route('/search_notes_tags', strict_slashes=False)
def search_note_tag():
    return render_template('search_n.html')


@app.route('/contacts', methods=['GET', 'POST'], strict_slashes=False)
def contacts():
    nick = user.get_user(session['user_id']['id']).nick
    contacts = contact.get_contacts_user(session['user_id']['id'])
    return render_template('/contacts.html', contacts=contacts, nick=nick, href_='contact',
                           amount_contacts=len(contacts))


@app.route('/add_contact', methods=['GET', 'POST'], strict_slashes=False)
def add_contact():
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
    nick = user.get_user(session['user_id']['id']).nick
    contacts = contact.get_contacts_user(session['user_id']['id'])
    birthday_date = 'dd/mm/yyyy'
    if request.method == 'POST':
        birthday_date = request.form.get('calendar')
        if birthday_date == '':
            flash('Choose date!')
            return redirect(request.url)
        contacts = contact.find_contact_birthday(
            session['user_id']['id'], birthday_date)
    return render_template('/contacts.html', contacts=contacts, nick=nick, href_='contact',
                           amount_contacts=len(contacts), calendar=birthday_date)


@app.route('/find_contact', methods=['GET', 'POST'], strict_slashes=False)
def find_contact():
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
    if request.method == 'POST':
        contact.cont_delete(contact_id, session['user_id']['id'])
        flash('Operation successfully!')
    return redirect(url_for('contacts'))


@app.route('/add_email/<contact_id>', methods=["POST"], strict_slashes=False)
def add_email(contact_id):
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
    contact_ = contact.get_contacts_user_by_id(
        session['user_id']['id'], contact_id)
    if request.method == 'POST':
        address = request.form.get('address')
        if request.form.get('address') is not None:
            contact.add_address(contact_id, address)
    return render_template('add_address.html', contact=contact_)


@app.route('/add_phone/<contact_id>', methods=["POST"], strict_slashes=False)
def add_phone(contact_id):
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
    nick = user.get_user(session['user_id']['id']).nick
    contact_ = contact.get_contacts_user_by_id(
        session['user_id']['id'], contact_id)
    if request.method == 'POST':
        pass
    return render_template('edit_contact.html', contact_id=contact_id, nick=nick, contact=contact_)


@app.route('/edit_name/<contact_id>', methods=['GET', 'POST'], strict_slashes=False)
def edit_name(contact_id):
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
    contact_ = contact.get_contacts_user_by_id(
        session['user_id']['id'], contact_id)
    if request.method == 'POST':
        if request.form.get('address') is not None:
            address = request.form.get('address')
            contact.update_address(contact_id, address_id, address)
    return render_template('edit_address.html', contact=contact_, address=address_id,
                           address_obj=contact.get_address(contact_id=contact_id, address_id=address_id)[0])
