git add LICENSE
git add *.py -A
git add *.in -A
git add *.cfg -A
git add *.sh -A
git add *.mo -A
git add *.po -A
git add .gitignore
git add *.md -A
git add *.rst -A
git add *.txt -A
git add *.png -A
git add ./flask_appbuilder -A
git add ./bin -A
git add ./babel -A
git add ./doc -A
git add ./examples -A
git add ./skeleton -A
git commit -m "$1"
git push origin master
