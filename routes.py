from flask import render_template, request, redirect, url_for, abort, flash
from werkzeug.security import check_password_hash
from flask_login import current_user, login_user, login_required
from forms import LoginForm, RegistrationForm, NewItemForm
from main import app, login_manager
from models import db, Item, User
from parser import parse_url


@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    form = RegistrationForm()
    if form.validate_on_submit():
        emails = list(map(str, db.session.query(User).all()))
        if form.email.data in emails:
            flash('email is already taken')
        else:
            user = User(
                email=form.email.data
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            form.email.data, form.password.data, form.confirm.data = '', '', ''
            return redirect(url_for('index'))
    return render_template('reg.html', title='Sign Up', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.query(User).filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('index'))
        else:
            return abort(400)
    return render_template('login.html', title='login', form=form)


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    add_form = NewItemForm()
    if add_form.validate_on_submit():
        url = add_form.field.data
        parse_data = parse_url(url)
        if parse_data != 'invalid url':
            service, product, price = parse_data
            item = Item(
                service=service,
                product=product,
                price=price,
                user_id=current_user.id
            )
            db.session.add(item)
            db.session.commit()
            add_form.field.data = ''
        else:
            flash('invalid url')
    data = db.session.query(Item).filter_by(user_id=current_user.id).all()
    return render_template('index.html', title='Home', data=data, add_form=add_form)


@app.route('/delete_item/<int:id>')
@login_required
def delete_item(id):
    item = Item.query.get(id)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('index'))


@login_manager.unauthorized_handler
def unauthorized():
    return render_template('unauthorized.html')


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port='8000')
