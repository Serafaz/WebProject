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
            if f'/static/img/{current_user}_image.png' not in images_of_players:
                return redirect('/load_photo')
        return render_template('login.html', message='Неправильный логин и пароль', form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/about_game', methods=['GET', 'POST'])
def about_game():
    if request.method == 'GET':
        return render_template('about_game.html')
    if request.method == 'POST':
        return redirect('/')


@app.route('/load_photo', methods=['GET', 'POST'])
def load_photo():
    if request.method == 'GET':
        return render_template('load_image_if_want.html', message='Выберите png-файл',
                               title='Загрузка фото')
    if request.method == 'POST':
        if request.files['file'].filename != '':
            f = request.files['file']
            if request.files['file'].filename[-4:] != '.png':
                return render_template('load_image_if_want.html', message='Файл не ".png"',
                                       title='Загрузка фото')
            filename = current_user + '_image.png'
            image = open(filename, 'wb')
            image.write(f.read())
            image.close()
            os.replace(filename, f'./static/img/{filename}')
        return redirect('/')


@app.route('/play/level1', methods=['GET', 'POST'])
def play_level1():
    return render_template('level1_template.html', title='Играем...')


def main():
    app.run()


if __name__ == "__main__":
    images_of_players = list()
    for currentdir, dirs, files in os.walk('./static/img'):
        for el in files:
            images_of_players.append(el)
    main()
