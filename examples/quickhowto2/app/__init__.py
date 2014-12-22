import logging
from flask import Flask
from flask.ext.appbuilder import SQLA, AppBuilder
from flask.ext.appbuilder.menu import Menu
#from sqlalchemy.engine import Engine
#from sqlalchemy import event

logging.basicConfig(format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')
logging.getLogger().setLevel(logging.DEBUG)

app = Flask(__name__)
app.config.from_object('config')
db = SQLA(app)
appbuilder = AppBuilder(app, db.session, menu=Menu(reverse=False))

"""
Only include this for SQLLite constraints

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
"""    
from flask import session, request, url_for, redirect, flash
from flask_oauth import OAuth
oauth = OAuth()
oauth_args = app.config.get('AUTH_OAUTH_PROVIDERS')[0]
flaskappbuilder = oauth.remote_app(oauth_args['name'], **oauth_args['remote_app'])

@flaskappbuilder.tokengetter
def get_twitter_token(token=None):
    print "TOKEN"
    return session.get('twitter_token')

@app.route('/loginoauth')
def login():
    print "OAUTH LOGIN"
    return flaskappbuilder.authorize(callback=url_for('oauth_authorized',
        next=request.args.get('next') or request.referrer or None))

@app.route('/oauth-authorized')
@flaskappbuilder.authorized_handler
def oauth_authorized(resp):
    print "OAUTH AUTORIZED"
    next_url = request.args.get('next') or url_for('index')
    if resp is None:
        flash(u'You denied the request to sign in.')
        return redirect(next_url)

    session['twitter_token'] = (
        resp['oauth_token'],
        resp['oauth_token_secret']
    )
    session['twitter_user'] = resp['screen_name']

    flash('You were signed in as %s' % resp['screen_name'])
    return redirect(next_url)


from app import views

