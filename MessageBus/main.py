import psycopg2
import time
import os
import sys
import stomp
from urllib import request, parse, error
import json



from listeners import ServiceRegistrationListener, MessageListener

conn = psycopg2.connect(host="postgres", port=5432, user="postgres")


time.sleep(3)


def start_products_listener(db, hosts):
    print("starting listener for products channel")

    queue = stomp.Connection(host_and_ports=hosts)
    queue.set_listener("", ProductsListener(db, hosts))
    queue.start()
    queue.connect(
        "products", "products", wait=True, headers={"client-id": "products-listener"}
    )
    queue.subscribe(
        destination="products",
        id=1,
        ack="auto",
        headers={
            "subscription-type": "MULTICAST",
            "durable-subscription-name": "someValue",
        },
    )

    print("sucesfully subscribed to 'products' channel")


def start_admin_listener(db, hosts):
    print("starting listener for administrator channel")
    queue2 = stomp.Connection(host_and_ports=hosts)
    queue2.set_listener("", AdminListener(db, hosts))
    queue2.start()
    queue2.connect("admin", "admin", wait=True, headers={"client-id": "admin-listener"})
    queue2.subscribe(
        destination="admin",
        id=1,
        ack="auto",
        headers={
            "subscription-type": "MULTICAST",
            "durable-subscription-name": "someValue",
        },
    )

    print("sucesfully subscribed to 'admin' channel")


def start_registry_listener(hosts):
    print("starting registry listener")
    queue = stomp.Connection(host_and_ports=hosts)
    registry = ServiceRegistrationListener(hosts)
    queue.set_listener("", registry)
    queue.start()
    queue.connect("register-new-service", "register-new-service", wait=True, headers={"client-id": "message-bus-registry"})
    queue.subscribe(
        destination="register-new-service",
        id=1,
        ack="auto",
        headers={
            "subscription-type": "MULTICAST",
            "durable-subscription-name": "someValue",
        },
    )
    return registry

def start_message_listener(hosts, registry):
    queue = stomp.Connection(host_and_ports=hosts)
    listener = MessageListener(hosts, registry)
    queue.set_listener("", listener)
    queue.start()
    queue.connect("message-bus-in", "message-bus-in", wait=True, headers={"client-id": "message-bus-listener"})
    queue.subscribe(
        destination="message-bus-in",
        id=1,
        ack="auto",
        headers={
            "subscription-type": "MULTICAST",
            "durable-subscription-name": "someValue",
        },
    )
    return listener

if __name__ == "__main__":
    print("starting message bus")
    hosts = [("queue", 61613)]
    registry = start_registry_listener(hosts)
    listener = start_message_listener(hosts, registry)

    while True:
        # keep app running to prevent docker from terminating
        time.sleep(0.01)
