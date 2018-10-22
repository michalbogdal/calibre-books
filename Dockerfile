FROM python:3.5
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
ADD requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt
RUN pip install https://github.com/unbit/uwsgi/archive/uwsgi-2.0.zip

ADD . /app
WORKDIR /app

EXPOSE 8000
CMD ["/app/compose/start.sh"]
