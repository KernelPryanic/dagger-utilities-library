FROM python:alpine

RUN apk add --update --no-cache git

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
