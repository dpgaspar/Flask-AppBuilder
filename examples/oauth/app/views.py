from flask import session, flash
from flask.ext.appbuilder.models.sqla.interface import SQLAInterface
from flask.ext.appbuilder import ModelView, SimpleFormView
from .forms import TweetForm
from app import appbuilder, db

class SendTweet(SimpleFormView):
    form = TweetForm
    form_title = 'Send a test tweet'

    message = 'Tweet sent!'

    def form_get(self, form):
        provider = session['oauth_provider']
        if not provider == 'twitter':
            flash('You must login with Twitter, this will not work', 'warning')
        form.message.data = "Flask-AppBuilder now supports OAuth!"

    def form_post(self, form):
        resp = self.appbuilder.sm.oauth_remotes['twitter'].post('statuses/update.json', data={
        'status': form.message.data
        })
        if resp.status != 200:
            flash('An error occurred', 'danger')
        else:
            flash(self.message, 'info')


appbuilder.add_view(SendTweet, "Tweet", icon="fa-twitter", label='Tweet')


db.create_all()


