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
            filename = str(current_user.id) + '_image.png'
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
    if request.method == 'GET':
        if current_user.is_authenticated:
            db_sess = db_session.create_session()
            user = db_sess.query(User).filter(User.id == current_user.id).first()
            arr_for_game = user.line_of_game
            if arr_for_game == '':
                arr_for_game = [''] * 46
            else:
                arr_for_game = arr_for_game.split('-')
                copy_arr_for_game = list()
                for el in arr_for_game:
                    if el == '/':
                        copy_arr_for_game.append('')
                    else:
                        copy_arr_for_game += el
                arr_for_game.clear()
                arr_for_game = copy_arr_for_game.copy()
            return render_template('level1_template.html', title='Играем...',
                                   filename='.' + current_user.filename_of_image,
                                   arr=arr_for_game)
        else:
            return redirect('/')
    if request.method == 'POST':
        if ((request.form['1'] == request.form['10'] == request.form['17'] == request.form['26'] ==
            request.form['41'] == '7') and (request.form['4'] == request.form['11'] ==
            request.form['31'] == request.form['40'] == request.form['46'] == '1') and
            (request.form['5'] == request.form['8'] == request.form['22'] == request.form['29'] ==
            request.form['45'] == '2') and (request.form['7'] == request.form['15'] ==
            request.form['19'] == request.form['32'] == request.form['39'] == '3') and
            (request.form['3'] == request.form['14'] == request.form['20'] == request.form['21'] ==
            request.form['28'] == request.form['38'] == '4') and (request.form['2'] ==
            request.form['6'] == request.form['35'] == request.form['37'] == request.form['44'] ==
            '5') and (request.form['13'] == request.form['18'] == request.form['25'] ==
            request.form['27'] == request.form['36'] == '6') and (request.form['24'] ==
            request.form['30'] == request.form['34'] == '8') and (request.form['9'] ==
            request.form['12'] == request.form['16'] == request.form['23'] ==
                request.form['33'] == request.form['42'] == request.form['43'] == '9')):
            db_sess = db_session.create_session()
            user = db_sess.query(User).filter(User.id == current_user.id).first()
            user.line_of_game = ''
            db_sess.commit()
            return render_template('already_complete.html', title='Победа!',
                                   filename='.' + current_user.filename_of_image)
        else:
            arr_of_values = list()
            for i in range(1, 47):
                if request.form[str(i)]:
                    if request.form[str(i)] != '-':
                        arr_of_values += request.form[str(i)]
                    else:
                        arr_of_values.append('/')
                else:
                    arr_of_values.append('/')
            db_sess = db_session.create_session()
            user = db_sess.query(User).filter(User.id == current_user.id).first()
            user.line_of_game = '-'.join(arr_of_values)
            db_sess.commit()
            return render_template('not_complete.html', title='Неверно',
                                   filename='.' + current_user.filename_of_image)


def main():
    db_session.global_init("db/comments.db")
    app.register_blueprint(comments_api.blueprint)
    app.run()


if __name__ == "__main__":
    main()
