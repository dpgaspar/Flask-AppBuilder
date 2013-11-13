pybabel extract -F ./babel/babel.cfg -k lazy_gettext -o ./babel/messages.pot .
pybabel update -i ./babel/messages.pot -d app/translations
pybabel compile -d app/translations


