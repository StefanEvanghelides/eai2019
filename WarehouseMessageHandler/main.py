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
    queue.start()
    queue.connect('products', 'products', wait=True, headers = {'client-id': 'products-listener'} )
    queue.subscribe(destination='products', id=1, ack='auto',headers = {'subscription-type': 'MULTICAST','durable-subscription-name':'someValue'})

    print("sucesfully subscribed to 'products' channel")


def start_admin_listener(db, hosts):
    print("starting listener for administrator channel")
    queue2 = stomp.Connection(host_and_ports=hosts)
    queue2.set_listener('', AdminListener(db, hosts))
    queue2.start()
    queue2.connect('admin', 'admin', wait=True, headers = {'client-id': 'admin-listener'} )
    queue2.subscribe(destination='admin', id=1, ack='auto',headers = {'subscription-type': 'MULTICAST','durable-subscription-name':'someValue'})
    
    print("sucesfully subscribed to 'admin' channel")


if __name__ == '__main__':
    hosts = [('queue', 61613)]
    conn = psycopg2.connect(host='postgres', port=5432, user='postgres')
    # start listeners for input channels
    start_products_listener(conn, hosts)
    start_admin_listener(conn, hosts)

    while True:
        # keep app running to prevent docker from terminating
        time.sleep(0.01)