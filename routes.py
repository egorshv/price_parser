from flask import render_template, request, redirect, url_for, abort, flash
from werkzeug.security import check_password_hash
from flask_login import current_user, login_user, login_required, logout_user
from forms import LoginForm, RegistrationForm, NewItemForm, GetNotifForm
from main import app, login_manager
from models import db, Item, User, ProductPrice
from parser import parse_url
from datetime import datetime


@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    form = RegistrationForm()
    if form.validate_on_submit():
        emails = list(map(str, db.session.query(User).all()))
        if form.email.data in emails:
            flash('email is already taken')
        else:
            user = User(
                email=form.email.data,
                get_notifications=False
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
                user_id=current_user.id,
                url=url
            )
            db.session.add(item)
            db.session.commit()
            add_form.field.data = ''
            product_price = ProductPrice(
                item_id=item.id,
                price=price,
                date=datetime.now()
            )
            db.session.add(product_price)
            db.session.commit()
        else:
            flash('invalid url')
    data = db.session.query(Item).filter_by(user_id=current_user.id).all()
    return render_template('index.html', title='Home', data=data, add_form=add_form)


@app.route('/delete_item/<int:item_id>')
@login_required
def delete_item(item_id):
    product_prices = db.session.query(ProductPrice).filter_by(item_id=item_id).all()
    for price in product_prices:
        db.session.delete(price)
    db.session.commit()
    item = Item.query.get(item_id)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = GetNotifForm()
    if form.validate_on_submit():
        user = User.query.get(current_user.id)
        user.get_notifications = form.notification.data
        db.session.commit()
    return render_template('settings.html', form=form, title='Settings')


@app.route('/chart/<int:item_id>')
@login_required
def chart(item_id):
    item = Item.query.get(item_id)
    data = db.session.query(ProductPrice).filter_by(item_id=item_id).all()
    prices = [i.price for i in data]
    dates = [i.date.strftime('%d-%m') for i in data]
    return render_template('chart.html', prices=prices, dates=dates, title=f'Chart for {item.product}')


@login_manager.unauthorized_handler
def unauthorized():
    return render_template('unauthorized.html')


@app.route('/log_out', methods=['GET', 'POST'])
@login_required
def log_out():
    logout_user()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port='5000')
