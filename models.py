from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(50))
    surname = db.Column(db.String(50))
    number = db.Column(db.String(50))
    country = db.Column(db.String(50))
    city = db.Column(db.String(50))
    file = db.Column(db.String(255))

    def __repr__(self):
        return f'<User {self.username}>'


class Child(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    data = db.Column(db.String(10))
    hobby = db.Column(db.String(20))
    id_user = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<Child {self.username}>'
