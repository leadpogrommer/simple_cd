import werkzeug.exceptions as exceptions
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from database.db import init_db
from resources.routes import init_routes

app = Flask(__name__)
app.config['MONGODB_SETTINGS'] = {
    'db': 'flask-test',
    'host': '127.0.0.1',
    'port': 27017
}
app.config['JWT_SECRET_KEY'] = '228'

bcrypt = Bcrypt(app)
jwt = JWTManager(app)
init_db(app)
init_routes(app)


@app.errorhandler(exceptions.HTTPException)
def handle_error(e: exceptions.HTTPException):
    return {"message": e.description}, e.code


if __name__ == '__main__':
    app.run(debug=True)

# есть система,
# в ней есть юзеры,
# у каждого может быть несколько проектов, каждый создает проект указывая название и репо
# (репо публичный, можно юзать пулл или клон, права не нужны)
# у каждого проекта есть конфиг config.{yml,json} или конфиг в бд
# в ней указана ветка, с которой необходимо забирать изменения, а после чего запускать указанную команду
# для каждого проекта каждого юзера должен быть способ остановки процесса через отправку любого пакета на условно какой то эндоинт по DELETE /control/{UNIQUE_PROJECT_ID}/runtime
# и способ перезапуска через отправку друго вида запроса на этот же эндпоинт
# т.е. ожидается полу-REST  механизм взаимодействия
# плюс по UPDATE /control/{...ID...}/runtime можно перезапустить проект (или запустить если не запущен)
# по DELETE /control/{...ID...} ожидается удаление проекта физически с диска
# по ПОСТ соответственно - инициализация и первая установка
