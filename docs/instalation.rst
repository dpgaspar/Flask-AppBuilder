Instalation
===========

3 Step instalation
----------------------

- Install it::

	pip install flask-appbuilder
	git clone https://github.com/dpgaspar/Flask-AppBuilder-Skeleton.git


- Configure it::

	python init_app.py

- Run it::

	python run.py

That's it!!

What requirements were instaled
-------------------------------

pip instalations installs all the requirements for you.

Flask App Builder dependes on

    - flask : The web framework, this is what were extending
    - flask-sqlalchemy : DB access see SQLAlchemy
    - flask-login : Login, session on flask.
    - flask-openid : Open ID authentication
    - flask-wtform
    - flask-Babel : For internationalization

If you plan to use Image on database, you will need to install PIL::

    pip install pillow
    
or::

    pip install PIL
