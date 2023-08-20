from flask import Flask, render_template, session, request, redirect, url_for
from flask_wtf import CSRFProtect

from HW_3.forms import LoginForm
from HW_3.model import db, User

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///userdatabase.db'
app.config['SECRET_KEY'] = b'fcece70bcec7aa11759a67571ed7ed0be61bf5dbf887a48216666875d57cf922'
csrf = CSRFProtect(app)

db.init_app(app)


@app.cli.command("init-db")
def init_db():
    db.create_all()


@app.cli.command("add-user")
def add_user():
    user = User(user_name='user111', user_lastname='user1111', user_password='111111', email="hg11k@jgkj.com")
    db.session.add(user)
    db.session.commit()


def get_main_menu(session):
    main_menu = [
        {'href': 'index', 'name': 'Главная'},
    ]
    if 'username' in session:
        main_menu.append({'href': 'login', 'name': 'Перезайти'})
        main_menu.append({'href': 'logoff', 'name': 'Выйти'})
    else:
        main_menu.append({'href': 'login', 'name': 'Вход'})
    return main_menu


@app.route('/')
@app.route('/index/')
def index():
    context = {
        'main_menu': get_main_menu(session)
    }
    if 'username' in session:
        context['username'] = {session["username"]}

    return render_template('index.html', **context)


@app.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST' and form.validate():
        user_name = form.user_name.data
        email = form.email.data
        password = form.password.data
        user_lastname = form.user_lastname.data
        user = User(user_name=user_name, user_lastname=user_lastname, user_password=password, email=email)
        print(user)
        db.session.add(user)
        db.session.commit()
        session['username'] = user_name
    context = {
        'main_menu': get_main_menu(session),
        'form': form,
    }
    return render_template('login.html', **context)


@app.route('/logoff/')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()
