import psycopg2
import time
import os
import sys
import stomp
from urllib import request, parse, error
import json


from listeners import ProductsListener, AdminListener

conn = psycopg2.connect(host='postgres', port=5432, user='postgres')


time.sleep(3)


def start_products_listener(db, hosts):
    print("starting listener for products channel")

    queue = stomp.Connection(host_and_ports=hosts)
    queue.set_listener('', ProductsListener(db, hosts))
    print(queue, queue.__class__, dir(queue))
    queue.start()
    queue.connect('admin', 'admin', wait=True, headers = {'client-id': 'warehouse-listener'} )
    queue.subscribe(destination='products', id=1, ack='auto',headers = {'subscription-type': 'MULTICAST','durable-subscription-name':'someValue'})

    print("sucesfully subscribed to 'products' channel")


def start_admin_listener(db, hosts):
    print("starting listener for administrator channel")
    queue2 = stomp.Connection(host_and_ports=hosts)
    queue2.set_listener('', AdminListener(db, hosts))
    queue2.start()
    queue2.connect('admin', 'admin', wait=True, headers = {'client-id': 'translator-listener'} )
    queue2.subscribe(destination='admin', id=1, ack='auto',headers = {'subscription-type': 'MULTICAST','durable-subscription-name':'someValue'})
    
    print("sucesfully subscribed to 'admin' channel")


if __name__ == '__main__':
    hosts = [('queue', 61613)]
    time.sleep(2)
    conn = psycopg2.connect(host='postgres', port=5432, user='postgres')
    # start listeners for input channels
    start_products_listener(conn, hosts)
    start_admin_listener(conn, hosts)

    while True:
        time.sleep(0.01)



    # urllib.urlopen('http://admin:admin@queue:8161/api/message?destination=queue://orders.input', {'body': 'test123'}) 
    # import stomp




    # time.sleep(3)
    # import requests
    # resp = requests.post('http://queue:8161/api/message?destination=topic://orders.input', data={'body': 'test123'}, auth=('admin', 'admin'))
    # print(resp)
    # print(resp.content)

    # time.sleep(2)
    # resp = requests.get('http://queue:8161/api/message?destination=topic://orders.input&clientId=warehouse&oneShot=true', auth=('admin', 'admin'))
    # print(resp)
    # print(resp.content)
    # proxy = req.ProxyHandler({'http': r'http://admin:admin@queue:8161'})
    # auth = req.HTTPBasicAuthHandler()
    # opener = req.build_opener(proxy, auth, req.HTTPHandler)
    # req.install_opener(opener)
    # conn = req.urlopen('http://admin:admin@queue:8161/api/message?destination=queue://orders.input')
    # return_str = conn.read()


 #    address = 'http://admin:admin@queue:8161/api/message?destination=queue://orders.input'

 #    req = request.Request(
 #        address,
 #        method="POST",
 #        data=parse.urlencode({'body': 'test123'}).encode("utf-8")
 #    )

 #    resp = request.urlopen(req)
 #    if not resp.getcode() == 200:
 #        print("ERR")
 #    else:
 #        print("SUCCES!")

 #    req = request.Request(
 #        address,
 #        method="GET"
 #    )

    # resp = request.urlopen(req)
    # print(resp)
    # cursor = conn.cursor()
    
    # print("creating demo table")
    # cursor.execute('CREATE TABLE IF NOT EXISTS demo (id SERIAL, name VARCHAR(64))')
    # print("inserting demo entry into demo table")
    # cursor.execute("INSERT INTO demo (name) VALUES ('test entry')")
    # cursor.execute("INSERT INTO demo (name) VALUES ('test entry2')")
    # print("querying demo table")
    # cursor.execute("SELECT * FROM demo")
    # result = cursor.fetchall()
    # conn.commit()
    # print(result)
    # conn.close()


    # time.sleep(5)

    # print("hello!")
    # conn = psycopg2.connect(host='postgres', port=5432, user='postgres')
    # cursor = conn.cursor()
    # print(conn)
    # print(cursor)
    # # print("dropping existing table")
    # # cursor.execute('DROP TABLE IF EXISTS demo')
    # print("creating demo table")
    # cursor.execute('CREATE TABLE IF NOT EXISTS demo (id SERIAL, name VARCHAR(64))')
    # print("inserting demo entry into demo table")
    # cursor.execute("INSERT INTO demo (name) VALUES ('test entry')")
    # print("querying demo table")
    # cursor.execute("SELECT * FROM demo")
    # result = cursor.fetchall()
    # print(result)
    # conn.close()