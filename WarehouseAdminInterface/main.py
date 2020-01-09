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


@app.route("/products/new", methods=["POST", "GET"])
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

        queue = stomp.Connection(host_and_ports=hosts)
        queue.start()
        queue.connect(
            "admin", "admin", wait=True, headers={"client-id": "warehouse-admin"}
        )
        message = json.dumps(
            {
                "type": "products",
                "action": "create",
                "content": {"product-name": product_name, "price": product_price},
            }
        )
        queue.send(body=message, destination="admin")
        queue.disconnect()
        app.logger.info("sent message")
        return render_template(
            "product_form.html", succes=True, product_name=product_name
        )


@app.route("/products/list", methods=["GET"])
def list_product():
    queue = stomp.Connection(host_and_ports=hosts)
    queue.start()
    queue.connect(
        "products",
        "products",
        wait=True,
        headers={"client-id": "warehouse-product-list"},
    )
    message = json.dumps(
        {
            "type": "products",
            "action": "list",
            "page": 1,
            "pageSize": 5,
            "sender": "admin-interface",
        }
    )
    queue.send(body=message, destination="products")
    queue.disconnect()
    return render_template(
        "request_list.html", success=True, message="requests product list"
    )


if __name__ == "__main__":
    print("hello!")
    create_demo_table(conn)
    seed_db(conn)

    app.run(debug=True, host="0.0.0.0", use_reloader=False)
