FROM python:2.7-alpine

MAINTAINER Kang Yufei "kyf0722@gmail.com"

ADD . /app

WORKDIR /app

RUN pip install -r requirements.txt
RUN apk update && apk add openssl && rm -r /var/cache/

EXPOSE 8080

VOLUME ['/config/']

ENTRYPOINT python SSLBumpProxy.py