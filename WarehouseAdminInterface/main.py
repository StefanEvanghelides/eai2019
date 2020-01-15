import psycopg2
import time
import os
import sys
import stomp
from urllib import request, parse, error
import json
from flask import Flask, request, render_template, redirect, send_from_directory
import random

app = Flask(__name__)
env_vars = dict(os.environ)
conn = psycopg2.connect(host="postgres", port=5432, user="postgres")
hosts = [("queue", 61613)]

# TO DO: send message to warehouse and move this impl to warehouse
# TO DO: split in DROP and CREATE action
def create_demo_table(conn):
    print("creating demo table")
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS demo")
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS demo (id SERIAL, name VARCHAR(64), price INTEGER)"
    )
    conn.commit()


# TO DO: send message to warehouse and move seeding to warehouse
def seed_db(conn):
    cursor = conn.cursor()

    name_seq = set(["test entry %d" % i for i in range(10)])

    cursor.execute(
        "SELECT * FROM demo WHERE name IN (%s)"
        % ", ".join(map(lambda item: "'%s'" % item, name_seq))
    )
    results = cursor.fetchall()
    existing = set([result[1] for result in results])
    to_insert = name_seq - existing
    print("seeding database")
    for name in to_insert:
        price = random.randint(1000, 10000)
        print("\t\tinserting entry with name <%s> and price <%d>" % (name, price))
        cursor.execute(
            "INSERT INTO demo (name, price) VALUES ('%s', %d)" % (name, price)
        )

    conn.commit()


# @app.route("/", methods=["POST", "GET"])
# def new_product():

#     app.logger.info("Create new product")
#     if request.method == "GET":
#         entries = []
#         return render_template("product_form.html")
#     else:
#         cursor = conn.cursor()
#         product_name = request.form.get("product-name")
#         product_price = request.form.get("product-price")
#         if not product_name or not product_price:
#             return render_template(
#                 "product_form.html",
#                 error=True,
#                 message="Product name or price is missing",
#             )

#         queue = stomp.Connection(host_and_ports=hosts)
#         queue.start()
#         queue.connect(
#             "admin",
#             "admin",
#             wait=True,
#             headers={"client-id": os.environ["HOSTNAME"] + "-new-product"},
#         )
#         message = json.dumps(
#             {
#                 "type": "products",
#                 "action": "create",
#                 "content": {"product-name": product_name, "price": product_price},
#             }
#         )
#         queue.send(body=message, destination="admin")
#         queue.disconnect()
#         app.logger.info("sent message")
#         return render_template(
#             "product_form.html", succes=True, product_name=product_name
#         )


# @app.route("/products/list", methods=["GET"])
# def list_product():
#     queue = stomp.Connection(host_and_ports=hosts)
#     queue.start()
#     queue.connect(
#         "products",
#         "products",
#         wait=True,
#         headers={"client-id": "warehouse-product-list"},
#     )
#     message = json.dumps(
#         {
#             "type": "products",
#             "action": "list",
#             "page": 1,
#             "pageSize": 5,
#             "sender": "admin-interface",
#         }
#     )
#     queue.send(body=message, destination="products")
#     queue.disconnect()
#     return render_template(
#         "request_list.html", success=True, message="requests product list"
#     )


# class MessageListener(stomp.ConnectionListener):
#     def __init__(self, hosts, *args, **kwargs):
#         super(MessageListener, self).__init__(*args, **kwargs)
#         # self.hosts = hosts
#         self.handlers_mapping = {"registration": self.handle_registration_confirmation}
#         # self.queue = stomp.Connection(host_and_ports=hosts)
#         # self.queue.start()
#         # self.queue.connect(
#         #     "reply", "reply", wait=True, headers={"client-id": "warehouse-listener"}
#         # )

#     def on_error(self, headers, message):
#         print('received an error "%s"' % message)

#     def on_message(self, headers, message):
#         print("RECEIVED MESSAGE!")
#         try:
#             parsed_message = json.loads(message)

#             handler = self.handlers_mapping[headers["subject"]]
#             handler(headers, parsed_message)

#             print('Warehouse products listener received a message "%s"' % message)
#         except Exception as e:
#             print(
#                 "An error occured while receiving a message in the 'Products' listener"
#             )
#             traceback.print_exc()

#     def handle_registration_confirmation(self, headers, message):
#         print("sucesfully received registration confirmation from message-bus")


# def start_message_listener():
#     print("SUBSCRIBE TO MESSAGE_BUS")
#     queue = stomp.Connection(host_and_ports=hosts)
#     queue.set_listener("", MessageListener(hosts))
#     queue.start()
#     queue.connect(
#         "admin",
#         "admin",
#         wait=True,
#         headers={"client-id": os.environ["HOSTNAME"] + "-listener"},
#     )
#     queue.subscribe(
#         destination="warehouse-admin-in",
#         id=1,
#         ack="auto",
#         headers={
#             "subscription-type": "MULTICAST",
#             "durable-subscription-name": "someValue",
#         },
#     )

#     print("sucesfully subscribed to 'warehouse-admin-in' channel")


# def register_at_message_bus():
#     print("BEGIN REGISTER AT MESSAGE BUS")
#     queue = stomp.Connection(host_and_ports=hosts)
#     queue.start()
#     queue.connect(
#         "admin", "admin", wait=True, headers={"client-id": os.environ["HOSTNAME"]}
#     )

#     headers = {
#         "type": "request",
#         "subject": "registration",
#         "sender": "warehouse-admin-interface",
#         "receiver": "message-bus",
#     }
#     body = {
#         "service-name": "warehouse-admin-interface",
#         "input-channel": "warehouse-admin-in",
#     }
#     queue.send(body=json.dumps(body), **headers, destination="register-new-service")
#     print("send registration request to message bus")


from Connection import Connection, Listener
c = Connection(
    "queue",
    "queue",
    61613,
    Listener(),
    "warehouse-admin-interface",
)

@app.route("/", methods=["POST", "GET"])
def new_product():

    app.logger.info("Create new product")
    if request.method == "GET":
        entries = []
        return render_template("product_form.html")
    else:
        cursor = conn.cursor()
        product_name = request.form.get("product-name")
        product_price = request.form.get("product-price")
        if not product_name or not product_price:
            return render_template(
                "product_form.html",
                error=True,
                message="Product name or price is missing",
            )

        headers = {
            "type": "request",
            "subject": "create-product",
            "sender": "warehouse-admin-interface",
            "receiver": "warehouse-message-handler"
        }

        body = {
            "product": {
                "price": product_price,
                "name": product_name
            }
        }

        queue = 'message-bus'

        c.send(queue, headers, body)
        app.logger.info("Sent new product to warehouse")
        return render_template(
            "product_form.html", succes=True, product_name=product_name
        )

@app.route("/create-database", methods=["GET", "POST"])
def create_db():
    app.logger.info("Create database")
    if request.method == "GET":
        entries = []
        return render_template("create_database.html")
    else:
        cursor = conn.cursor()
        drop_if_exists = request.form.get("drop-if-exists")

        headers = {
            "type": "request",
            "subject": "create-database",
            "sender": "warehouse-admin-interface",
            "receiver": "warehouse-message-handler"
        }

        body = {
            "dropIfExists": drop_if_exists
        }

        queue = 'message-bus'

        c.send(queue, headers, body)
        return render_template(
            "create_database.html", succes=True
        )

@app.route("/seed-db", methods=["GET", "POST"])
def seed_db():
    app.logger.info("Seed database")
    if request.method == "GET":
        entries = []
        return render_template("seed_database.html")
    else:
        cursor = conn.cursor()
        number_of_products = request.form.get("number-of-products")
        min_price = request.form.get("min-price")
        max_price = request.form.get("max-price")

        headers = {
            "type": "request",
            "subject": "seed-database",
            "sender": "warehouse-admin-interface",
            "receiver": "warehouse-message-handler"
        }

        body = {
            "numberOfProducts": number_of_products,
            "minPrice": min_price,
            "maxPrice": max_price
        }

        queue = 'message-bus'

        c.send(queue, headers, body)
        return render_template(
            "seed_database.html", succes=True
        )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", use_reloader=False)
    



    # time.sleep(2)
    # print("hello!")
    # create_demo_table(conn)
    # seed_db(conn)
    # register_at_message_bus()
    # start_message_listener()

