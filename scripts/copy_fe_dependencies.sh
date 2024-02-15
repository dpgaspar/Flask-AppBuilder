#!/bin/bash

SOURCE_BASE_PATH="node_modules"
TARGET_BASE_PATH="flask_appbuilder/static/appbuilder"

echo - Copying JQuery
cp ${SOURCE_BASE_PATH}/jquery/dist/jquery.min.js ${TARGET_BASE_PATH}/js/jquery-latest.js

echo - Copying bootstrap
cp ${SOURCE_BASE_PATH}/bootstrap/dist/js/bootstrap.min.js ${TARGET_BASE_PATH}/js/bootstrap.min.js
cp ${SOURCE_BASE_PATH}/bootstrap/dist/css/bootstrap.min.css.map ${TARGET_BASE_PATH}/css/bootstrap.min.css.map
cp ${SOURCE_BASE_PATH}/bootstrap/dist/css/bootstrap.min.css ${TARGET_BASE_PATH}/css/bootstrap.min.css

echo - Copying select2
cp ${SOURCE_BASE_PATH}/select2/dist/js/select2.min.js ${TARGET_BASE_PATH}/js/select2/select2.min.js
cp ${SOURCE_BASE_PATH}/select2/dist/css/select2.min.css ${TARGET_BASE_PATH}/css/select2/select2.min.css
cp ${SOURCE_BASE_PATH}/select2/dist/css/select2.min.css ${TARGET_BASE_PATH}/css/select2/select2.min.css
cp ${SOURCE_BASE_PATH}/select2-bootstrap-theme/dist/select2-bootstrap.min.css ${TARGET_BASE_PATH}/css/select2/select2-bootstrap.min.css

echo - Copying font Awesome
cp ${SOURCE_BASE_PATH}/@fortawesome/fontawesome-free/css/*.min.css ${TARGET_BASE_PATH}/css/fontawesome/
cp ${SOURCE_BASE_PATH}/@fortawesome/fontawesome-free/webfonts/* ${TARGET_BASE_PATH}/css/webfonts/

echo - Copying world flags
cp ${SOURCE_BASE_PATH}/world-flags-sprite/stylesheets/flags16.css ${TARGET_BASE_PATH}/css/flags/flags16.css
cp ${SOURCE_BASE_PATH}/world-flags-sprite/images/flags16.png ${TARGET_BASE_PATH}/css/images/flags16.png

echo - Copying bootstrap datepicker
cp ${SOURCE_BASE_PATH}/bootstrap-datepicker/dist/css/bootstrap-datepicker3.min.css ${TARGET_BASE_PATH}/css/bootstrap-datepicker/bootstrap-datepicker3.min.css
cp ${SOURCE_BASE_PATH}/bootstrap-datepicker/dist/js/bootstrap-datepicker.min.js ${TARGET_BASE_PATH}/js/bootstrap-datepicker/bootstrap-datepicker.min.js
