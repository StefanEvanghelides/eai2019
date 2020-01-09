FROM python:3.7

RUN pip install psycopg2
RUN pip install requests
RUN pip install stomp.py

RUN mkdir /app
COPY . /app

ENTRYPOINT python3 -u /app/main.py
