import sqlalchemy.exc
from flask import render_template, request, flash, redirect, url_for, session, make_response
from . import app
from src.repository import user, tag, note


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


@app.route('/Notebook', strict_slashes=False)
def notebook():
    nick = user.get_user(session['user_id']['id'])
    all_tags_n = len(tag.all_tags(nick.id))
    all_tags = tag.all_tags(nick.id)
    all_notes = note.all_notes(nick.id)
    all_notes_n = len(note.all_notes(nick.id))
    return render_template('notebook.html', nick=nick, all_tags_num=all_tags_n, all_tags=all_tags, all_notes=all_notes,
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
