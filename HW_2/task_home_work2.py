from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = b'fcece70bcec7aa11759a67571ed7ed0be61bf5dbf887a48216666875d57cf922'


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
    context = {
        'main_menu': get_main_menu(session)
    }
    if request.method == 'POST':
        session['username'] = request.form.get('username')
        session['email'] = request.form.get('email')
        return redirect(url_for('index'))
    return render_template('login.html', **context)


@app.route('/logoff/')
def logout():
    session.pop('username', None)
    session.pop('email', None)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()
