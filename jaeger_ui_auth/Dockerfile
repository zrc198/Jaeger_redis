FROM python:3.12.7-alpine

COPY requirements.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt

COPY src  .
CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:8080", "--certfile=flask.crt", "--keyfile=flask.key", "app:app"]

