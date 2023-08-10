from flask import Flask, render_template

app = Flask(__name__)

MAIN_MENU = [
            {'href': 'index', 'name': 'Главная'},
            {'href': 'about', 'name': 'О компании'},
            {'href': 'product', 'name': 'Продукция',
                'second_menu': [
                    {'href': 'clothes', 'name': 'Одежда'},
                    {'href': 'shoes', 'name': 'Обувь'},
                ]
             },
            {'href': 'contact', 'name': 'Контакты'},
        ]

@app.route('/')
@app.route('/<name_page>/')
def pages(name_page='index'):
    context = {
        'main_menu': MAIN_MENU,
    }
    print(name_page)
    return render_template(f'{name_page}.html', **context)

if __name__ == '__main__':
    app.run()
