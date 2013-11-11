./git_upload "$1"
python setup.py sdist upload
pip uninstall flask-appbuilder
pip install flask-appbuilder
