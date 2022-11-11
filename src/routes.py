import sqlalchemy.exc
from flask import render_template, request, flash, redirect, url_for, session, make_response
from . import app
from src.repository import user, tag


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
    #contacts = contact.get_all_contacts(session['user_id']['id'])
    #contact_notes = notes.get_all_notes(session['user_id']['id'])
    return render_template('account_window.html', nick=nick)


@app.route('/Notebook', strict_slashes=False)
def notebook():
    all_tags = tag.all_tags()
    nick = user.get_user(session['user_id']['id']).nick
    # print(user.get_user(session['user_id']['id']).id)
    return render_template('notebook.html', nick=nick, all_tags=all_tags)


@app.route('/tags', methods=['GET', 'POST'], strict_slashes=False)
def tags():

    nick = user.get_user(session['user_id']['id']).nick
    if request.method == "POST":
        tag_name = request.form.get("tag_name")
        tag.add_tag(tag_name)
    return render_template('tags.html', nick=nick)


@app.route('/notes', strict_slashes=False)
def notes():
    nick = user.get_user(session['user_id']['id']).nick
    return render_template('notes.html', nick=nick)

