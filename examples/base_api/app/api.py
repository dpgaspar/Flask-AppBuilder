from flask import request
from flask_appbuilder.api import BaseApi, expose, rison, safe
from flask_appbuilder.security.decorators import protect

from . import appbuilder

greeting_schema = {"type": "object", "properties": {"name": {"type": "string"}}}


class ExampleApi(BaseApi):

    resource_name = "example"
    apispec_parameter_schemas = {"greeting_schema": greeting_schema}

    @expose("/greeting")
    def greeting(self):
        """Send a greeting
        ---
        get:
          responses:
            200:
              description: Greet the user
              content:
                application/json:
                  schema:
                    type: object
                    properties:
                      message:
                        type: string
        """
        return self.response(200, message="Hello")

    @expose("/greeting2", methods=["POST", "GET"])
    def greeting2(self):
        """Send a greeting
        ---
        get:
          responses:
            200:
              description: Greet the user
              content:
                application/json:
                  schema:
                    type: object
                    properties:
                      message:
                        type: string
        post:
          responses:
            201:
              description: Greet the user
              content:
                application/json:
                  schema:
                    type: object
                    properties:
                      message:
                        type: string
        """
        if request.method == "GET":
            return self.response(200, message="Hello (GET)")
        return self.response(201, message="Hello (POST)")

    @expose("/greeting3")
    @rison()
    def greeting3(self, **kwargs):
        if "name" in kwargs["rison"]:
            return self.response(
                200, message="Hello {}".format(kwargs["rison"]["name"])
            )
        return self.response_400(message="Please send your name")

    @expose("/greeting4")
    @rison(greeting_schema)
    def greeting4(self, **kwargs):
        """Get item from Model
        ---
        get:
          parameters:
          - $ref: '#/components/parameters/greeting_schema'
          responses:
            200:
              description: Greet the user
              content:
                application/json:
                  schema:
                    type: object
                    properties:
                      message:
                        type: string
        """
        return self.response(200, message="Hello {}".format(kwargs["rison"]["name"]))

    @expose("/risonjson")
    @rison()
    def rison_json(self, **kwargs):
        """Say it's risonjson
        ---
        get:
          responses:
            200:
              description: Say it's private
              content:
                application/json:
                  schema:
                    type: object
        """
        return self.response(200, result=kwargs["rison"])

    @expose("/private")
    @protect()
    def private(self):
        """Say it's private
        ---
        get:
          responses:
            200:
              description: Say it's private
              content:
                application/json:
                  schema:
                    type: object
            401:
              $ref: '#/components/responses/401'
        """
        return self.response(200, message="This is private")

    @expose("/error")
    @protect()
    @safe
    def error(self):
        """Error 500
        ---
        get:
          responses:
            500:
              $ref: '#/components/responses/500'
        """
        raise Exception


appbuilder.add_api(ExampleApi)
