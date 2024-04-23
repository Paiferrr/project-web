from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, current_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from models import User, Child, db
from PIL import Image
import io
import sqlite3

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = 'secret-key-goes-here'
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    else:
        return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('profile'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        name = None
        surname = None
        number = None
        country = None
        city = None
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already taken')
        else:
            hashed_password = generate_password_hash(password)
            new_user = User(username=username, password=hashed_password, email=email, name=name, surname=surname,
                            number=number, country=country, city=city)
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully')
            return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/profile')
def profile():
    if current_user.is_authenticated:
        if db.session.query(User).filter_by(username=current_user.username).first().name is None:
            return render_template('profile.html', user=current_user, data=False, file='images/default.jpg')
        else:
            if db.session.query(User).filter_by(username=current_user.username).first().file == b'' or \
                db.session.query(User).filter_by(username=current_user.username).first().file is None:
                return render_template('profile.html', user=current_user, data=True, file='images/default.jpg')
            else:
                image_data = db.session.query(User).filter_by(username=current_user.username).first().file
                image = Image.open(io.BytesIO(image_data))
                image.save(f"static\images\{current_user.username}.png")
            return render_template('profile.html', user=current_user, data=True, file=f'images/{current_user.username}.png')
    else:
        return redirect(url_for('login'))


@app.route("/edit_profile")
def edit_profile():
    pass


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/edit', methods=['GET', 'POST'])
def edit():
    fi = False
    if request.method == 'POST' and request.form.get('child_name') is None:
        name = request.form['name']
        surname = request.form['surname']
        number = request.form['number']
        country = request.form['country']
        city = request.form['city']
        file = request.files['file']
        f = file.read()

        user = User.query.filter_by(username=current_user.username).first()
        user.name = name
        user.surname = surname
        user.number = number
        user.country = country
        user.city = city
        user.file = f

        db.session.commit()
        if request.form.get('checkbox') == 'on':
            return render_template('child.html', user=current_user)
        else:
            return redirect(url_for('profile'))

    elif request.method == 'POST':
        name = request.form['child_name']
        surname = request.form['child_surname']
        data = request.form['data']
        hobby = request.form.get('group')
        id_user = db.session.query(User).filter_by(username=current_user.username).first().id
        if db.session.query(Child).filter_by(id_user=id_user).first() is None:
            new_child = Child(name=name, surname=surname, data=data, id_user=id_user, hobby=hobby)
            db.session.add(new_child)
            db.session.commit()
    if current_user.is_authenticated:
        name = db.session.query(User).filter_by(username=current_user.username).first().name
        if name is not None:
            reg = True
        else:
            reg = False
        if db.session.query(Child).first() is not None:
            id_user = db.session.query(User).filter_by(username=current_user.username).first().id
            fi = []
            for i in db.session.query(Child).filter_by(id_user=id_user).all():
                fi.append(f'{i.name} {i.surname} - {i.hobby}')
        if db.session.query(User).filter_by(username=current_user.username).first().file == b'' or \
                db.session.query(User).filter_by(username=current_user.username).first().file is None:
            return render_template('edit_profile.html', user=current_user, reg=reg, child=fi, file='images/default.jpg')
        else:
            image_data = db.session.query(User).filter_by(username=current_user.username).first().file
            image = Image.open(io.BytesIO(image_data))
            image.save(f"static\images\{current_user.username}.png")
        return render_template('edit_profile.html', user=current_user, reg=reg, child=fi, file=f'images/{current_user.username}.png')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)