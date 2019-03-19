from flask import request
from flask_appbuilder.api import BaseApi, expose, rison, safe
from flask_appbuilder.security.decorators import protect
from . import appbuilder


class MyFirstApi(BaseApi):

    resource_name = 'myfirst'
    version = 'v2'
    route_base = '/newapi/v3/nice'

    @expose('/greeting')
    def greeting(self):
        return self.response(200, message="Hello")

    @expose('/greeting2', methods=['POST', 'GET'])
    def greeting2(self):
        if request.method == 'GET':
            return self.response(200, message="Hello (GET)")
        return self.response(201, message="Hello (POST)")

    @expose('/greeting3')
    @rison
    def greeting3(self, **kwargs):
        if 'name' in kwargs['rison']:
            return self.response(
                200,
                message="Hello {}".format(kwargs['rison']['name'])
            )
        return self.response_400(message="Please send your name")

    @expose('/risonjson')
    @rison
    def rison_json(self, **kwargs):
        return self.response(200, result=kwargs['rison'])

    @expose('/private')
    @protect
    def private(self):
        return self.response(200, message="This is private")

    @expose('/error')
    @protect
    @safe
    def error(self):
        raise Exception


appbuilder.add_view_no_menu(MyFirstApi)
