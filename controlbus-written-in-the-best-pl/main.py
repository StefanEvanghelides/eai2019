import psycopg2
import time
import os
import sys
import stomp
from urllib import request, parse, error
import json


from listeners import ServiceRegistrationListener, MessageListener

time.sleep(2)


# def start_registry_listener(hosts):
#     print("starting registry listener")
#     queue = stomp.Connection(host_and_ports=hosts)
#     registry = ServiceRegistrationListener(hosts)
#     queue.set_listener("", registry)
#     queue.start()
#     queue.connect(
#         "register-new-service",
#         "register-new-service",
#         wait=True,
#         headers={"client-id": "message-bus-registry"},
#     )
#     queue.subscribe(
#         destination="register-new-service",
#         id=1,
#         ack="auto",
#         headers={
#             "subscription-type": "MULTICAST",
#             "durable-subscription-name": "someValue",
#         },
#     )
#     return registry


def start_message_listener(hosts):
    queue = stomp.Connection(host_and_ports=hosts)
    listener = MessageListener(hosts)
    listener.set_queue(queue)
    queue.set_listener("", listener)
    queue.start()
    queue.connect(
        "admin",
        "admin",
        wait=True,
        headers={"client-id": "control-bus-listener"},
    )
    queue.subscribe(
        destination="control-bus-in",
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
    time.sleep(5)
    hosts = [("control-queue", 61613)]
    #registry = start_registry_listener(hosts)
    listener = start_message_listener(hosts)
    print("started message listener")
    while True:
        # keep app running to prevent docker from terminating
        time.sleep(0.01)
