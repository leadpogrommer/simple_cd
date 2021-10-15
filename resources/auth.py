import datetime

from flask import request
from flask.views import MethodView
from flask_jwt_extended import create_access_token

from database.models import User


class SignupApi(MethodView):
    def post(self):
        body = request.get_json()
        user = User()
        user.username = body['username']
        user.set_password(body['password'])
        user.save()
        return {"status": "ok"}


class LoginApi(MethodView):
    def post(self):
        body = request.get_json()
        user = User.objects.get(username=body['username'])
        authorized = user.check_password(body.get('password'))
        if not authorized:
            return {'error': 'Email or password invalid'}, 401

        expires = datetime.timedelta(days=7)
        access_token = create_access_token(identity=str(user.id), expires_delta=expires)
        return {'token': access_token}, 200
