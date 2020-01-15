import psycopg2
import json
from flask import Flask, request, render_template

app = Flask(__name__)


from Connection import Connection, Listener

c = Connection(
    "main-queue", "control-queue", 61613, Listener(), "warehouse-admin-interface"
)


@app.route("/", methods=["POST", "GET"])
def new_product():

    app.logger.info("Create new product")
    if request.method == "GET":
        entries = []
        return render_template("product_form.html")
    else:
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
            "receiver": "warehouse-message-handler",
        }

        body = {"product": {"price": product_price, "name": product_name}}

        queue = "message-bus"

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
        drop_if_exists = request.form.get("drop-if-exists")

        headers = {
            "type": "request",
            "subject": "create-database",
            "sender": "warehouse-admin-interface",
            "receiver": "warehouse-message-handler",
        }

        body = {"dropIfExists": drop_if_exists}

        queue = "message-bus"

        c.send(queue, headers, body)
        return render_template("create_database.html", succes=True)


@app.route("/seed-db", methods=["GET", "POST"])
def seed_db():
    app.logger.info("Seed database")
    if request.method == "GET":
        entries = []
        return render_template("seed_database.html")
    else:
        number_of_products = request.form.get("number-of-products")
        min_price = request.form.get("min-price")
        max_price = request.form.get("max-price")

        headers = {
            "type": "request",
            "subject": "seed-database",
            "sender": "warehouse-admin-interface",
            "receiver": "warehouse-message-handler",
        }

        body = {
            "numberOfProducts": number_of_products,
            "minPrice": min_price,
            "maxPrice": max_price,
        }

        queue = "message-bus"

        c.send(queue, headers, body)
        return render_template("seed_database.html", succes=True)


@app.route("/test-switch-queue", methods=["GET", "POST"])
def test_switch_queue():
    pass


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", use_reloader=False)
