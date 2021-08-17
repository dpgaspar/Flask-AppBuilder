echo #
echo Removing old dist files
echo #
rm -Rf ./dist
echo #
echo Generating dist
echo #
python setup.py sdist bdist_wheel
echo #
echo Upload to Pypi
echo #
twine upload dist/*

