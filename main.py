import datetime
from flask import Flask, render_template, request, make_response, session, redirect, abort, jsonify
from data import db_session, comments_api
from data.users import User
from data.comments import Comment
from forms.user import RegisterForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms.login import LoginForm
from forms.comment import CommentForm
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
    if current_user.is_authenticated:
        return render_template('main.html', title='Судоку',
                               filename=current_user.filename_of_image)
    else:
        return render_template('main.html', title='Судоку',
                               filename="./static/img/image_of_user.png")


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)


@app.route('/comments')
def comments():
    db_sess = db_session.create_session()
    comments = db_sess.query(Comment).all()
    if current_user.is_authenticated:
        return render_template('comments.html', title='Комментарии', comments=comments,
                               filename=current_user.filename_of_image)
    else:
        return render_template('comments.html', title='Комментарии', comments=comments,
                               filename="./static/img/image_of_user.png")


@app.route('/comment', methods=['GET', 'POST'])
@login_required
def add_comment():
    form = CommentForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        comment = Comment(title=form.title.data,
                          content=form.content.data)
        current_user.comments.append(comment)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/comments')
    if current_user.is_authenticated:
        return render_template('comment.html', title='Добавление комментария', form=form,
                               filename=current_user.filename_of_image)
    else:
        return render_template('comment.html', title='Добавление комментария', form=form,
                               filename="./static/img/image_of_user.png")


@app.route('/comment/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_comment(id):
    form = CommentForm()
    if request.method == 'GET':
        db_sess = db_session.create_session()
        comment = db_sess.query(Comment).filter(Comment.id == id,
                                                Comment.user == current_user).first()
        form.title.data = comment.title
        form.content.data = comment.content
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        comment = db_sess.query(Comment).filter(Comment.id == id,
                                                Comment.user == current_user).first()
        if comment:
            comment.title = form.title.data
            comment.content = form.content.data
            db_sess.commit()
            return redirect('/comments')
        else:
            abort(404)
    if current_user.is_authenticated:
        return render_template('comment.html', title='Редактирование комментария', form=form,
                               filename=current_user.filename_of_image)
    else:
        return render_template('comment.html', title='Редактирование комментария', form=form,
                               filename="./static/img/image_of_user.png")


@app.route("/comment_del/<int:id>", methods=['GET', 'POST'])
@login_required
def comment_del(id):
    db_sess = db_session.create_session()
    comment = db_sess.query(Comment).filter(Comment.id == id, Comment.user == current_user).first()
    if comment:
        db_sess.delete(comment)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/comments')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            if current_user.is_authenticated:
                return render_template('register.html', title='Регистрация',
                                       form=form, message='Пароли не совпадают',
                                       filename=current_user.filename_of_image)
            else:
                return render_template('register.html', title='Регистрация',
                                       form=form, message='Пароли не совпадают',
                                       filename="./static/img/image_of_user.png")
        if len(form.password.data) < 8:
            if current_user.is_authenticated:
                return render_template('register.html', title='Регистрация',
                                       form=form, message='Пароль должен быть больше семи символов',
                                       filename=current_user.filename_of_image)
            else:
                return render_template('register.html', title='Регистрация',
                                       form=form, message='Пароль должен быть больше семи символов',
                                       filename="./static/img/image_of_user.png")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            if current_user.is_authenticated:
                return render_template('register.html', title='Регистрация',
                                       form=form, message='Пользователь уже есть',
                                       filename=current_user.filename_of_image)
            else:
                return render_template('register.html', title='Регистрация',
                                       form=form, message='Пользователь уже есть',
                                       filename="./static/img/image_of_user.png")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    if current_user.is_authenticated:
        return render_template('register.html', title='Регистрация', form=form,
                               filename=current_user.filename_of_image)
    else:
        return render_template('register.html', title='Регистрация', form=form,
                               filename="./static/img/image_of_user.png")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect('/load_photo')
        if current_user.is_authenticated:
            return render_template('login.html', message='Неправильный логин и пароль', form=form,
                                   filename=current_user.filename_of_image)
        else:
            return render_template('login.html', message='Неправильный логин и пароль', form=form,
                                   filename="./static/img/image_of_user.png")
    if current_user.is_authenticated:
        return render_template('login.html', title='Авторизация', form=form,
                               filename=current_user.filename_of_image)
    else:
        return render_template('login.html', title='Авторизация', form=form,
                               filename="./static/img/image_of_user.png")


@app.route('/about_game', methods=['GET', 'POST'])
def about_game():
    if request.method == 'GET':
        if current_user.is_authenticated:
            return render_template('about_game.html', title='Об игре',
                                   filename=current_user.filename_of_image)
        else:
            return render_template('about_game.html', title='Об игре',
                                   filename="./static/img/image_of_user.png")
    if request.method == 'POST':
        return redirect('/')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/load_photo', methods=['GET', 'POST'])
def load_photo():
    if request.method == 'GET':
        if current_user.is_authenticated:
            return render_template('load_image_if_want.html', message='Выберите png-файл',
                                   title='Загрузка фото',
                                   filename=current_user.filename_of_image)
        else:
            return render_template('load_image_if_want.html', message='Выберите png-файл',
                                   title='Загрузка фото',
                                   filename="./static/img/image_of_user.png")
    if request.method == 'POST':
        if request.files['file'].filename != '':
            f = request.files['file']
            if request.files['file'].filename[-4:] != '.png':
                if current_user.is_authenticated:
                    return render_template('load_image_if_want.html', message='Файл не ".png"',
                                           title='Загрузка фото',
                                           filename=current_user.filename_of_image)
                else:
                    return render_template('load_image_if_want.html', message='Файл не ".png"',
                                           title='Загрузка фото',
                                           filename="./static/img/image_of_user.png")
            filename = current_user.name + '_image.png'
            image = open(filename, 'wb')
            image.write(f.read())
            image.close()
            os.replace(filename, f'./static/img/{filename}')
            db_sess = db_session.create_session()
            user = db_sess.query(User).filter(User.name == current_user.name).first()
            user.filename_of_image = f'./static/img/{filename}'
            db_sess.commit()
        return redirect('/')


@app.route('/play/level1', methods=['GET', 'POST'])
def play_level1():
    return render_template('level1_template.html', title='Играем...')


def main():
    db_session.global_init("db/comments.db")
    app.register_blueprint(comments_api.blueprint)
    app.run()


if __name__ == "__main__":
    main()
