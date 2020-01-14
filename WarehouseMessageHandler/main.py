import psycopg2
import time
import os
import sys
import stomp
from urllib import request, parse, error
import json
import math
import traceback

from Connection import Connection, Listener
from functools import partial


def list_products(db, message, headers, queues):
    cursor = db.cursor()

    limit = message["pageSize"]
    offset = max(0, message["page"] - 1) * limit

    cursor.execute("SELECT * FROM demo LIMIT %d OFFSET %d" % (limit, offset))
    result = cursor.fetchall()
    cursor.execute("SELECT COUNT(*) FROM demo")
    total_count = cursor.fetchall()[0][0]  # returns list of tuples for some reason

    has_next = offset + limit < total_count
    has_previous = offset > 0

    headers = {
        "type": "response",
        "subject": "products",
        "sender": "warehouse-message-handler",
        "receiver": headers["sender"],
    }

    body = {
        "pageInfo": {
            "page": message["page"],
            "pageSize": message["pageSize"],
            "hasNextPage": has_next,
            "hasPreviousPage": has_previous,
            "pageCount": math.ceil(total_count / limit),
        },
        "products": result,
    }

    queues["message-bus"].send(
        body=json.dumps(body), headers=headers, destination="message-bus-in"
    )


if __name__ == "__main__":
    conn = psycopg2.connect(host="postgres", port=5432, user="postgres")
    request_handlers = {"list-products": partial(list_products, conn)}
    c = Connection(
        "queue",
        "queue",
        61613,
        Listener(request_handlers=request_handlers),
        "warehouse-message-handler",
    )
    # hosts = [("queue", 61613)]
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
