echo #
echo Removing old build artifacts
echo #
rm -Rf ./dist ./build
echo #
echo Generating dist
echo #
python -m build
echo #
echo Upload to Pypi
echo #
twine upload dist/*
