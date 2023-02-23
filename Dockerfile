# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /app

COPY /init .
RUN pip3 install -r requirements.txt



ENTRYPOINT python3 hello.py