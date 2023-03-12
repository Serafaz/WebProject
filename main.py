import datetime
from flask import Flask, render_template, request, make_response, session, redirect
from data import db_session
from data.users import User
from forms.user import RegisterForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms.login import LoginForms
from forms.news import NewsForm

app = Flask(__name__)
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=31)
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
def index():
    return render_template('base.html', title='Главная')


def main():
    app.run()


if __name__ == "__main__":
    main()
