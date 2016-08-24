FROM python:3.5.1

COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt
RUN pip install coveralls pymongo==2.8 flask-mongoengine==0.7.1 Pillow
