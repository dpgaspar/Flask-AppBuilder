from flask import g, request, current_app
from flask.ext.login import current_user
from flask import flash, redirect,url_for
from models import is_item_public




