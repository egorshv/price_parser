from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from main import db, login_manager


class Item(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    service = db.Column(db.String(20), nullable=False)
    product = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f'Item {self.id}'


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(120), nullable=False)
    items = db.relationship('Item', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def __repr__(self):
        return f'{self.email}'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
