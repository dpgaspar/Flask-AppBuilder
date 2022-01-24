User Registration
=================

Allows users to register themselves as users, will behave differently according to the authentication method.

Database Authentication
-----------------------

Using database authentication (auth db) the login screen will present a new 'Register' option where the
user is directed to a form where he/she fill's a form with the necessary login/user information.
The form includes a Recaptcha field to ensure a human is filling the form. After the form is correctly filled
by the user an email is sent to the user with a link with an URL containing a hash belonging to his/her registration.

If the URL is accessed the user is inserted into the F.A.B user model and activated.

This behaviour can be easily configured or completely altered. By overriding the **RegisterUserDBView** properties.
or implementing an all new class. **RegisterUserDBView** inherits from BaseRegisterUser that hold some handy base methods
and properties.

Note that the process required for sending email's uses the excellent flask-mail package so make sure you installed it
first.

Enabling and using the default implementation is easy just configure the following global config keys on config.py::

    AUTH_TYPE = AUTH_DB
    AUTH_USER_REGISTRATION = True
    AUTH_USER_REGISTRATION_ROLE = 'Public'
    # Config for Flask-WTF Recaptcha necessary for user registration
    RECAPTCHA_PUBLIC_KEY = 'GOOGLE PUBLIC KEY FOR RECAPTCHA'
    RECAPTCHA_PRIVATE_KEY = 'GOOGLE PRIVATE KEY FOR RECAPTCHA'
    # Config for Flask-Mail necessary for user registration
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'yourappemail@gmail.com'
    MAIL_PASSWORD = 'passwordformail'
    MAIL_DEFAULT_SENDER = 'fabtest10@gmail.com'


OpenID Authentication
---------------------

Registering a user when using OpenID authentication is very similar to database authentication, but this time
all the basic necessary information is fetched from the provider and presented to the user to alter it (or not)
and submit.

LDAP Authentication
-------------------

LDAP user self registration is automatic, no register user option is shown. All users are registered, and the
required information is fetched from the LDAP server.

Configuration
-------------

You can configure the default behaviour and UI on many different ways. The easiest one is making your own RegisterUser
class and inherit from RegisterUserDBView (when using auth db). Let's take a look at a practical example::

    from flask_appbuilder.security.registerviews import RegisterUserDBView

    class MyRegisterUserDBView(RegisterUserDBView):
        email_template = 'register_mail.html'
        email_subject = lazy_gettext('Your Account activation')
        activation_template = 'activation.html'
        form_title = lazy_gettext('Fill out the registration form')
        error_message = lazy_gettext('Not possible to register you at the moment, try again later')
        message = lazy_gettext('Registration sent to your email')


This class will override:

 - The template used to generate the email sent by the user. Take a look at the default template to get a simple
   starting point `Mail template <https://github.com/dpgaspar/Flask-AppBuilder/blob/master/flask_appbuilder/templates/appbuilder/general/security/register_mail.html>`_.
   Your template will receive the following parameters:

    - first_name
    - last_name
    - username
    - url

 - The email subject

 - The activation template. This the page shown to the user when he/she finishes the activation. Take a look at the default template to get a simple
   starting point `Activation Template <https://github.com/dpgaspar/Flask-AppBuilder/blob/master/flask_appbuilder/templates/appbuilder/general/security/activation.html>`_.

 - The form title. The title that is presented on the registration form.

 - Message is the success message presented to the user when an email was successfully sent to him and his registration
   was recorded.

After defining your own class, override SecurityManager class and set the **registeruserdbview** property
with your own class::

    class MySecurityManager(SecurityManager):
        registeruserdbview = MyRegisterUserDBView

Then tell F.A.B. to use your security manager class, take a look at the :doc:`security` on how to do it.
