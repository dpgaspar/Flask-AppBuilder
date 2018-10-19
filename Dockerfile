FROM python:3.5.1

WORKDIR /app

COPY . .

RUN python setup.py install
RUN pip install coveralls pymongo==2.8 flask-mongoengine==0.7.1 Pillow
