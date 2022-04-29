
FROM python:2.7

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

COPY . /app

CMD [ "python", "status.py", "c012~d48e7bd045032ccd626c3dcce5c997ad" ]