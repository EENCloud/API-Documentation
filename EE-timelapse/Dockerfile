
FROM python:3.7.2-slim

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN apt-get update

RUN apt-get install ffmpeg -y --allow-unauthenticated

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

COPY . /app


CMD [ "./startup.sh" ]