from flask import render_template, request, flash, redirect, url_for, session, make_response
from . import app
from src.repository import user, contact
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
    return 'I am worhing'


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
    politics_news = politics.parse_finance(10)
    football_news = football.parse_football(10)
    weather_news = weather.parse_weather('Днепр')
    currency_news = currency.parse_currency()
    return render_template('account_window.html', nick=nick,
                           politics_news=politics_news,
                           football_news=football_news,
                           weather_news=weather_news,
                           currency_news=currency_news)


@app.route('/contacts', methods=['GET', 'POST'], strict_slashes=False)
def contacts():
    nick = user.get_user(session['user_id']['id']).nick
    contacts = contact.get_contacts_user(session['user_id']['id'])
    # for contact1 in contacts:
    #     print(contact1.emails)
    #     for email in contact1.emails:
    #         print(email.email)

    # print(contacts.emails)
    return render_template('/contacts.html', contacts=contacts,nick=nick, href_='contact', amount_contacts=len(contacts)) 
    return render_template('contacts.html', nick=nick)


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
        validation = contact_validation(first_name=first_name, last_name=last_name,birthday=birthday, email=email, address=address, phone=cell_phone)
        if validation != None:
            flash(validation)
            return redirect(request.url)

        print(first_name, last_name,birthday,email,address,cell_phone)
        contact.create_contact(first_name, last_name, birthday, email, address, cell_phone, session['user_id']['id'])
    return render_template('add_contact.html', nick=nick)

@app.route('/delete_contact/<contact_id>', methods=["POST"], strict_slashes=False)
def contact_delete(contact_id):
    if request.method == 'POST':
        contact.cont_delete(contact_id, session['user_id']['id'])
        flash('Operation successfully!')
    return redirect(url_for('contacts'))

# @app.route('/add_email', methods=["POST"], strict_slashes=False)
# def add_email():
#     return render_template('add_email.html')


@app.route('/add_email/<contact_id>', methods=["POST"], strict_slashes=False)
def add_email(contact_id):
    contact_ = contact.get_contacts_user_by_id(session['user_id']['id'], contact_id)
    if request.method == 'POST':
        if request.form.get('email') != None:
            email = request.form.get('email')
            validation = contact_validation(email=email)
            if validation != None:
                flash(validation[:-1])
                return render_template('add_email.html', contact=contact_)
            contact.add_email(contact_id, email)
            print("email = ", email)
        print('contact_id = ', contact_id)
        print("session = ", session['user_id']['id'])
    return render_template('add_email.html', contact=contact_)

@app.route('/add_address/<contact_id>', methods=["POST"], strict_slashes=False)
def add_address(contact_id):
    contact_ = contact.get_contacts_user_by_id(session['user_id']['id'], contact_id)
    if request.method == 'POST':
        address = request.form.get('address')
        if request.form.get('address') != None:
            contact.add_address(contact_id, address)
        print('contact_id = ', contact_id)
        print("address = ", address)
        print("session = ", session['user_id']['id'])
    return render_template('add_address.html', contact=contact_)

@app.route('/add_phone/<contact_id>', methods=["POST"], strict_slashes=False)
def add_phone(contact_id):
    contact_ = contact.get_contacts_user_by_id(session['user_id']['id'], contact_id)
    if request.method == 'POST':
        phone = request.form.get('phone')
        if request.form.get('phone') != None:
            validation = contact_validation(phone=phone)
            if validation != None:
                flash(validation[:-1])
                return render_template('add_phone.html', contact=contact_)
            contact.add_phone(contact_id, phone)
        print('contact_id = ', contact_id)
        print("phone = ", phone)
        print("session = ", session['user_id']['id'])
    return render_template('add_phone.html', contact=contact_)

@app.route('/edit_contact/<contact_id>', methods=["POST"], strict_slashes=False)
def edit_contact(contact_id):
    nick = user.get_user(session['user_id']['id']).nick
    contact_ = contact.get_contacts_user_by_id(session['user_id']['id'], contact_id)
    if request.method == 'POST':
        pass
    # return render_template('/contacts.html', contacts=contacts,nick=nick, href_='contact') 
    return render_template('edit_contact.html', contact_id=contact_id, nick=nick, contact=contact_)

@app.route('/edit_name/<contact_id>', methods=['GET', 'POST'], strict_slashes=False)
def edit_name(contact_id):
    print("Im in edit_name")
    contact_ = contact.get_contacts_user_by_id(session['user_id']['id'], contact_id)
    print(request.method)
    if request.method == 'POST':
        if request.form.get('name') != None:
            print('contact_id = ', contact_id)
            name = request.form.get('name')
            print('name = ', name)
            contact.update_first_name(contact_id, session['user_id']['id'], name)
    return render_template('edit_name.html', contact=contact_,first_name_obj=contact_.first_name)

@app.route('/edit_last_name/<contact_id>', methods=['GET', 'POST'], strict_slashes=False)
def edit_last_name(contact_id):
    contact_ = contact.get_contacts_user_by_id(session['user_id']['id'], contact_id)
    print(request.method)
    if request.method == 'POST':
        if request.form.get('last_name') != None:
            print('contact_id = ', contact_id)
            last_name = request.form.get('last_name')
            print('last_name = ', last_name)
            contact.update_last_name(contact_id, session['user_id']['id'], last_name)
    return render_template('edit_last_name.html', contact=contact_,last_name_obj=contact_.last_name)

@app.route('/edit_birthday/<contact_id>', methods=['GET', 'POST'], strict_slashes=False)
def edit_birthday(contact_id):
    contact_ = contact.get_contacts_user_by_id(session['user_id']['id'], contact_id)
    print(request.method)
    if request.method == 'POST':
        if request.form.get('birthday') != None:
            print('contact_id = ', contact_id)
            birthday = request.form.get('birthday')
            validation = contact_validation(birthday=birthday)
            if validation != None:
                flash(validation[:-1])
                return render_template('edit_birthday.html', contact=contact_, birthday_obj=contact_.birthday)
            print('birthday = ', birthday)
            contact.update_birthday(contact_id, session['user_id']['id'], birthday)
    return render_template('edit_birthday.html', contact=contact_, birthday_obj=contact_.birthday)

@app.route('/edit_email/<contact_id>/<email_id>', methods=['GET', 'POST'], strict_slashes=False)
def edit_email(contact_id, email_id):
    contact_ = contact.get_contacts_user_by_id(session['user_id']['id'], contact_id)
    print(request.method)
    if request.method == 'POST':
        if request.form.get('email') != None:
            email = request.form.get('email')
            validation = contact_validation(email=email)
            if validation != None:
                flash(validation[:-1])
                return render_template('edit_email.html', contact=contact_, email=email_id, email_obj=contact.get_email(contact_id=contact_id,email_id=email_id)[0])
            contact.update_email(contact_id, email_id, email)
        # print('contact_id = ', contact_id)
        # print('email_id = ', email_id)
    return render_template('edit_email.html', contact=contact_, email=email_id, email_obj=contact.get_email(contact_id=contact_id,email_id=email_id)[0])

@app.route('/edit_phone/<contact_id>/<phone_id>', methods=['GET', 'POST'], strict_slashes=False)
def edit_phone(contact_id, phone_id):
    contact_ = contact.get_contacts_user_by_id(session['user_id']['id'], contact_id)
    if request.method == 'POST':
        if request.form.get('phone') != None:
            phone = request.form.get('phone')
            validation = contact_validation(phone=phone)
            if validation != None:
                flash(validation[:-1])
                return render_template('edit_phone.html', contact=contact_, phone=phone_id, phone_obj=contact.get_phone(contact_id=contact_id,phone_id=phone_id)[0])
            # print('email = ', email)
            contact.update_phone(contact_id, phone_id, phone)
        # print('contact_id = ', contact_id)
        # print('email_id = ', email_id)
    return render_template('edit_phone.html', contact=contact_, phone=phone_id, phone_obj=contact.get_phone(contact_id=contact_id,phone_id=phone_id)[0])

@app.route('/edit_address/<contact_id>/<address_id>', methods=['GET', 'POST'], strict_slashes=False)
def edit_address(contact_id, address_id):
    contact_ = contact.get_contacts_user_by_id(session['user_id']['id'], contact_id)
    if request.method == 'POST':
        if request.form.get('address') != None:
            address = request.form.get('address')
            # print('email = ', email)
            contact.update_address(contact_id, address_id, address)
        # print('contact_id = ', contact_id)
        # print('email_id = ', email_id)
    return render_template('edit_address.html', contact=contact_, address=address_id, address_obj=contact.get_address(contact_id=contact_id,address_id=address_id)[0])




