Release protocol
----------------

1 - Create a release branch named `release/<VERSION>`

2 - Update CHANGELOG.rst with all the changes since last release (use: `git log --pretty=format:"%s [%an]"`)

3 - Bump version on `flask_appbuilder/__init__.py`

4 - Submit PR and check all tests pass

5 - tag latest commit with `v<VERSION>` ex: v2.1.8

6 - merge PR

7 - checkout and pull master branch

8 - Upload package to PyPI: `python -m build && twine upload dist/*`

9 - Update readthedocs with the new master version
