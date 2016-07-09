FROM python:3-alpine

ADD . /usr/local/app
WORKDIR /usr/local/app

RUN pip install -r requirements.txt

CMD ./moderation-bot.py
