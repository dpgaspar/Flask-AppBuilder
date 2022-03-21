BREAKING CHANGES
================

Version 4.0.0
-------------

- Drops python 3.6 support
- Removed config key `AUTH_STRICT_RESPONSE_CODES`, it's always strict now.
- Removes `Flask-OpenID` dependency (you can install it has an extra dependency `pip install flask-appbuilder[openid]`)
- Major version bumps on following packages

**Flask from 1.X to 2.X**

Breaking changes: https://flask.palletsprojects.com/en/2.0.x/changes/#version-2-0-0

**flask-jwt-extended 3.X to 4.X:**

Breaking changes: https://flask-jwt-extended.readthedocs.io/en/stable/v4_upgrade_guide/

**Jinja2 2.X to 3.X**

Breaking changes: https://jinja.palletsprojects.com/en/3.0.x/changes/#version-3-0-0

**Werkzeug 1.X to 2.X**

https://werkzeug.palletsprojects.com/en/2.0.x/changes/#version-2-0-0

The following packages are probably not impactful to you:

**pyJWT  1.X to 2.X:**

Breaking changes: https://pyjwt.readthedocs.io/en/stable/changelog.html#v2-0-0

**Click  7.X to 8.X:**

Breaking changes:  https://click.palletsprojects.com/en/8.0.x/changes/#version-8-0-0

**itsdangerous 1.X to 2.X**

Breaking changes: https://github.com/pallets/itsdangerous/blob/main/CHANGES.rst#version-200

Version 3.0.0 (OAuth)
---------------------

Major version 3, changed it's **OAuth** dependency from flask-oauth to authlib, due to this OAuth configuration
changed:

Before:

.. code-block::

    OAUTH_PROVIDERS = [
        {'name':'google', 'icon':'fa-google', 'token_key':'access_token',
            'remote_app': {
                'consumer_key':'GOOGLE KEY',
                'consumer_secret':'GOOGLE SECRET',
                'base_url':'https://www.googleapis.com/oauth2/v2/',
                'request_token_params':{
                  'scope': 'email profile'
                },
                'request_token_url':None,
                'access_token_url':'https://accounts.google.com/o/oauth2/token',
                'authorize_url':'https://accounts.google.com/o/oauth2/auth'}
        }
    ]

Now:

.. code-block::

    OAUTH_PROVIDERS = [
        {'name':'google', 'icon':'fa-google', 'token_key':'access_token',
            'remote_app': {
                'client_id':'GOOGLE KEY',
                'client_secret':'GOOGLE SECRET',
                'api_base_url':'https://www.googleapis.com/oauth2/v2/',
                'client_kwargs':{
                  'scope': 'email profile'
                },
                'request_token_url':None,
                'access_token_url':'https://accounts.google.com/o/oauth2/token',
                'authorize_url':'https://accounts.google.com/o/oauth2/auth'}
        }
    ]

Also make sure you change your dependency for flask-oauth to `authlib <https://github.com/lepture/authlib>`_
