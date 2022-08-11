from flask import session, flash
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder import ModelView, SimpleFormView
from .forms import TweetForm
from app import appbuilder, db


class SendTweet(SimpleFormView):
    form = TweetForm
    form_title = "Send a test tweet"

    message = "Tweet sent!"

    def form_get(self, form):
        provider = session["oauth_provider"]
        if not provider == "twitter":
            flash("You must login with Twitter, this will not work", "warning")
        form.message.data = "Flask-AppBuilder now supports OAuth!"

    def form_post(self, form):
        remote_app = self.appbuilder.sm.oauth_remotes["twitter"]
        resp = remote_app.post(
            "statuses/update.json",
            data={"status": form.message.data},
            token=remote_app.token,
        )
        if resp.status_code != 200:
            flash("An error occurred", "danger")
        else:
            flash(self.message, "info")


"""
Example of a decorator to override the OAuth provider information getter

@appbuilder.sm.oauth_user_info_getter
def get_oauth_user_info(sm, provider, response=None):
# for GITHUB
    if provider == 'github' or provider == 'githublocal':
        me = sm.oauth_remotes[provider].get('user')
        return {'username': "github_" + me.json().get('login')}
    # for twitter
    if provider == 'twitter':
        me = sm.oauth_remotes[provider].get('account/settings.json')
        return {'username': "twitter_" + me.json().get('screen_name', '')}
    # for linkedin
    if provider == 'linkedin':
        me = sm.oauth_remotes[provider].get('people/~:(id,email-address,first-name,last-name)?format=json')
        data = me.json()
        return {'username': "linkedin_" + data.get('id', ''),
                'email': data.get('email-address', ''),
                'first_name': data.get('firstName', ''),
                'last_name': data.get('lastName', '')}
    # for Google
    if provider == 'google':
        me = sm.oauth_remotes[provider].get('userinfo')
        data = me.json()
        return {'username': data.get('id', ''),
                'first_name': data.get('given_name', ''),
                'last_name': data.get('family_name', ''),
                'email': data.get('email', '')}
"""


appbuilder.add_view(SendTweet, "Tweet", icon="fa-twitter", label="Tweet")


db.create_all()
