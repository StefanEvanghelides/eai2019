FROM python:3.7

RUN pip install psycopg2
RUN pip install requests
RUN pip install stomp.py
RUN pip3 install flask

RUN mkdir /app
COPY . /app

RUN ls /app

ENTRYPOINT python3 /app/main.py
