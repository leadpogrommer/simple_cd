# from flask_restful import Api
from flask import Flask

from resources.auth import LoginApi, SignupApi
from resources.ci import CreatorApi, ProjectApi, RuntimeApi


def init_routes(app: Flask):
    app.add_url_rule('/control', view_func=CreatorApi.as_view('create'))
    app.add_url_rule('/control/<id>', view_func=ProjectApi.as_view('project'))
    app.add_url_rule('/control/<id>/runtime', view_func=RuntimeApi.as_view('runtime'))

    app.add_url_rule('/login', view_func=LoginApi.as_view('login'))
    app.add_url_rule('/signup', view_func=SignupApi.as_view('signup'))
