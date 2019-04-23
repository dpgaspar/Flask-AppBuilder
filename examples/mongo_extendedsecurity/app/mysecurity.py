# -*- coding: utf-8 -*-
"""
Flask-Appbuilder security extension with mongoengine
adapted from http://flask-appbuilder.readthedocs.io/en/latest/security.html?highlight=user#extending-the-user-model
"""
import datetime
from mongoengine import (
    DateTimeField,
    StringField,
    ReferenceField,
    ListField,
    BooleanField,
    IntField,
)
from flask_appbuilder.security.mongoengine.manager import SecurityManager
from flask_appbuilder.security.mongoengine.models import User
from flask_appbuilder.security.views import UserDBModelView
from flask_babel import lazy_gettext


#
# Subclass the appbuilder User to add extra fields to the User model
#
class MyUser(User):
    extra = StringField()


class MyUserDBModelView(UserDBModelView):
    """
        View that add DB specifics to User view.
        Override to implement your own custom view.
        Then override userdbmodelview property on SecurityManager
    """

    show_fieldsets = [
        (
            lazy_gettext("User info"),
            {"fields": ["username", "active", "roles", "login_count", "extra"]},
        ),
        (
            lazy_gettext("Personal Info"),
            {"fields": ["first_name", "last_name", "email"], "expanded": True},
        ),
        (
            lazy_gettext("Audit Info"),
            {
                "fields": [
                    "last_login",
                    "fail_login_count",
                    "created_on",
                    "created_by",
                    "changed_on",
                    "changed_by",
                ],
                "expanded": False,
            },
        ),
    ]

    user_show_fieldsets = [
        (
            lazy_gettext("User info"),
            {"fields": ["username", "active", "roles", "login_count", "extra"]},
        ),
        (
            lazy_gettext("Personal Info"),
            {"fields": ["first_name", "last_name", "email"], "expanded": True},
        ),
    ]

    add_columns = [
        "first_name",
        "last_name",
        "username",
        "active",
        "email",
        "roles",
        "extra",
        "password",
        "conf_password",
    ]
    list_columns = ["first_name", "last_name", "username", "email", "active", "roles"]

    edit_columns = [
        "first_name",
        "last_name",
        "username",
        "active",
        "email",
        "roles",
        "extra",
    ]


#
# My Security Manager
#
class MySecurityManager(SecurityManager):
    user_model = MyUser
    userdbmodelview = MyUserDBModelView
