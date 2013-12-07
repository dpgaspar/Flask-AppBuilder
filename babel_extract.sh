pybabel extract -F ./babel/babel.cfg -k lazy_gettext -o ./babel/messages.pot .
pybabel update -i ./babel/messages.pot -d flask_appbuilder/translations
pybabel compile -d flask_appbuilder/translations


