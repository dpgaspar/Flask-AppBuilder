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
        resp = self.appbuilder.sm.oauth_remotes["twitter"].post(
            "statuses/update.json", data={"status": form.message.data}
        )
        if resp.status != 200:
            flash("An error occurred", "danger")
        else:
            flash(self.message, "info")


"""
Example of an decorator to override the OAuth provider information getter

@appbuilder.sm.oauth_user_info_getter
def get_oauth_user_info(sm, provider, response=None):
# for GITHUB
    if provider == 'github' or provider == 'githublocal':
        me = sm.oauth_remotes[provider].get('user')
        return {'username': "github_" + me.data.get('login')}
    # for twitter
    if provider == 'twitter':
        me = sm.oauth_remotes[provider].get('account/settings.json')
        return {'username': "twitter_" + me.data.get('screen_name', '')}
    # for linkedin
    if provider == 'linkedin':
        me = sm.oauth_remotes[provider].get('people/~:(id,email-address,first-name,last-name)?format=json')
        return {'username': "linkedin_" + me.data.get('id', ''),
                'email': me.data.get('email-address', ''),
                'first_name': me.data.get('firstName', ''),
                'last_name': me.data.get('lastName', '')}
    # for Google
    if provider == 'google':
        me = sm.oauth_remotes[provider].get('userinfo')
        return {'username': me.data.get('id', ''),
                'first_name': me.data.get('given_name', ''),
                'last_name': me.data.get('family_name', ''),
                'email': me.data.get('email', '')}
"""


appbuilder.add_view(SendTweet, "Tweet", icon="fa-twitter", label="Tweet")


db.create_all()
