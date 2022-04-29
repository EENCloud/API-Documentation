
FROM python:3.7.2

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

COPY . /app

CMD [ "python", "Listen_for_thumbnails.py"]
