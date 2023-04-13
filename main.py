import datetime
from flask import Flask, render_template, request, make_response, session, redirect
from data import db_session
from data.users import User
from forms.user import RegisterForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms.login import LoginForm
import os

app = Flask(__name__)
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=31)
app.config['SECRET_KEY'] = 'nonogramms_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
def index():
    return render_template('main.html', title='Нонограммы')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if len(form.password.data) < 8:
            return render_template('register.html', title='Регистрация',
                                   form=form, message='Длина пароля должна быть хотя бы 8 символов')
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form, message='Пароли не совпадают')
        # db_sess = db_session.create_session()
        # if db_sess.query(User).filter(User.email == form.email.data).first():
        #    return render_template('register.html', title='Регистрация',
        #                           form=form, message='Пользователь уже есть')
        '''user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()'''
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect('/load_photo')
        return render_template('login.html', message='Неправильный логин и пароль', form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/load_photo', methods=['GET', 'POST'])
def load_photo():
    if request.method == 'GET':
        return render_template('load_image_if_want.html', title='Загрузка фото')
    if request.method == 'POST':
        f = request.files['file']
        filename = current_user + 'f'
        image = open(filename, 'wb')
        image.write(f.read())
        image.close()
        os.replace(filename, f'static/img/{filename}')
        return redirect('/')


def main():
    app.run()


if __name__ == "__main__":
    main()
