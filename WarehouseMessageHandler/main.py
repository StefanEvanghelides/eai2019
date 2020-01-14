import psycopg2
import time
import os
import sys
import stomp
from urllib import request, parse, error
import json
import math
import traceback
from listeners import ProductsListener, AdminListener
from Connection import Connection, Listener

conn = psycopg2.connect(host="postgres", port=5432, user="postgres")

time.sleep(3)


class MessageListener(stomp.ConnectionListener):
    def __init__(self, db, hosts, queue, *args, **kwargs):
        super(MessageListener, self).__init__(*args, **kwargs)
        # self.hosts = hosts
        self.db = db
        self.queue = queue
        self.handlers_mapping = {
            "registration": self.handle_registration_confirmation,
            "products": self.handle_products
        }
        self.product_action_handlers = {
            'list': self.list
        }
        # self.queue = stomp.Connection(host_and_ports=hosts)
        # self.queue.start()
        # self.queue.connect(
        #     "reply", "reply", wait=True, headers={"client-id": "warehouse-listener"}
        # )

    def on_error(self, headers, message):
        print('received an error "%s"' % message)

    def on_message(self, headers, message):
        try:
            parsed_message = json.loads(message)

            handler = self.handlers_mapping[headers["subject"]]
            handler(headers, parsed_message)

            print('Warehouse products listener received a message "%s"' % message)
        except Exception as e:
            print(
                "An error occured while receiving a message in the 'Products' listener"
            )
            traceback.print_exc()

    def handle_registration_confirmation(self, headers, message):
        print("sucesfully received registration confirmation from message-bus")

    def handle_products(self, headers, message):
        action_handler = self.product_action_handlers[message['action']]
        action_handler(headers, message)

    def list(self, headers, message):
        print("Warehouse received message: ", message)
        cursor = self.db.cursor()
        limit = message["pageSize"]
        offset = max(0, message["page"] - 1) * limit
        cursor.execute("SELECT * FROM demo LIMIT %d OFFSET %d" % (limit, offset))
        result = cursor.fetchall()
        cursor.execute("SELECT COUNT(*) FROM demo")
        total_count = cursor.fetchall()[0][0]  # returns list of tuples for some reason
        print(offset, limit, total_count)
        has_next = offset + limit < total_count
        has_previous = offset > 0

        headers = {
        'type': 'response',
        'subject': 'products',
        'sender': 'warehouse-message-handler',
        'receiver': headers['sender']
        }
        body = {
            'pageInfo': {
                "page": message["page"],
                "pageSize": message["pageSize"],
                "hasNextPage": has_next,
                "hasPreviousPage": has_previous,
                "pageCount": math.ceil(total_count / limit),
            },
            'products': result
        }

        self.queue.send(body=json.dumps(body), headers=headers, destination="message-bus-in")
        print("Warehouse sent products to reply channel", message)



def start_message_listener(conn, hosts, send_queue):
    print("starting listener for administrator channel")
    queue = stomp.Connection(host_and_ports=hosts)
    queue.set_listener("", MessageListener(conn, hosts, send_queue))
    queue.start()
    queue.connect("admin", "admin", wait=True, headers={"client-id": os.environ['HOSTNAME'] + "-listener"})
    queue.subscribe(
        destination="warehouse-message-in",
        id=1,
        ack="auto",
        headers={
            "subscription-type": "MULTICAST",
            "durable-subscription-name": "someValue",
        },
    )

    print("sucesfully subscribed to 'warehouse-message-in' channel")

def register_at_message_bus(hosts, queue):
    headers = {
        'type': 'request',
        'subject': 'registration',
        'sender': 'warehouse-message-handler',
        'receiver': 'message-bus'
    }
    body = {
        'service-name': 'warehouse-message-handler',
        'input-channel': 'warehouse-message-in'
    }
    queue.send(
        body=json.dumps(body),
        **headers,
        destination="register-new-service"
    )

    print("send registration request to message bus")


def list_products(self, headers, message):
    print("Warehouse received message: ", message)
    cursor = self.db.cursor()
    limit = message["pageSize"]
    offset = max(0, message["page"] - 1) * limit
    cursor.execute("SELECT * FROM demo LIMIT %d OFFSET %d" % (limit, offset))
    result = cursor.fetchall()
    cursor.execute("SELECT COUNT(*) FROM demo")
    total_count = cursor.fetchall()[0][0]  # returns list of tuples for some reason
    print(offset, limit, total_count)
    has_next = offset + limit < total_count
    has_previous = offset > 0

    headers = {
    'type': 'response',
    'subject': 'products',
    'sender': 'warehouse-message-handler',
    'receiver': headers['sender']
    }
    body = {
        'pageInfo': {
            "page": message["page"],
            "pageSize": message["pageSize"],
            "hasNextPage": has_next,
            "hasPreviousPage": has_previous,
            "pageCount": math.ceil(total_count / limit),
        },
        'products': result
    }

    self.message_bus.send(body=json.dumps(body), headers=headers, destination="message-bus-in")
    print("Warehouse sent products to reply channel", message)



if __name__ == "__main__":
    request_handlers = {
        'list': list_products
    }
    c = Connection('queue', 'queue', 61613, Listener(request_handlers=request_handlers), 'warehouse-message-handler')
    # hosts = [("queue", 61613)]
    # conn = psycopg2.connect(host="postgres", port=5432, user="postgres")
    # # start listeners for input channels
    # queue = stomp.Connection(host_and_ports=hosts)
    # queue.start()
    # queue.connect("admin", "admin")
    # register_at_message_bus(hosts, queue)
    # start_message_listener(conn, hosts, queue)
    # start_products_listener(conn, hosts)
    # start_admin_listener(conn, hosts)

    while True:
        # keep app running to prevent docker from terminating
        time.sleep(0.01)
