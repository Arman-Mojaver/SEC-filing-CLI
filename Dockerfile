FROM python:3.9.11-slim-buster

ADD requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

ADD . /app/
WORKDIR /app/