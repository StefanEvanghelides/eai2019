import json
import math
import random


"""
 message = {
    "page": 1 <= Integer <= ceil(product_count / page_size),
    "pageSize": 1 <= Integer <= product_count
 }
"""


def list_products(db, message, headers, queues):
    message = json.loads(message)
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
        "subject": "list-products",
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


"""
message = {
    product: {
        "price": Integer,
        "name": String
    }
}
"""


def create_product(db, message, headers, queues):
    cursor = db.cursor()
    message = json.loads(message)
    print(message)
    name = message["product"]["name"]
    price = int(message["product"]["price"])

    cursor.execute("INSERT INTO demo (name, price) VALUES ('%s', %d)" % (name, price))

    db.commit()
    print("Created product {'name': %s, 'price': %d}" % (name, price))


"""
message = {
    "dropIfExists": Boolean
}
"""


def create_db(db, message, headers, queues):
    cursor = db.cursor()
    message = json.loads(message)

    if message["dropIfExists"] == "on":
        print("Dropping old demo table")
        cursor.execute("DROP TABLE IF EXISTS demo")
        db.commit()

    print("Creating demo table")
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS demo (id SERIAL, name VARCHAR(64), price INTEGER)"
    )

    headers = {
        "type": "response",
        "subject": "create-database",
        "sender": "warehouse-message-handler",
        "receiver": headers["sender"],
    }
    # TO DO: actually send confirmation
    # body = {"created": True}

    # queues["message-bus"].send(
    #     body=json.dumps(body), headers=headers, destination="message-bus-in"
    # )


"""
message = {
    "numberOfProducts": Integer,
    "minPrice": Integer,
    "maxPrice": Integer
}
"""


def seed_db(db, message, headers, queues):
    message = json.loads(message)
    cursor = db.cursor()

    name_seq = set(["Demo Product %d" % i for i in range(int(message["numberOfProducts"]))])
    print("\n\n\n", name_seq, "\n\n\n")
    cursor.execute(
        "SELECT * FROM demo WHERE name IN (%s)"
        % ", ".join(map(lambda item: "'%s'" % item, name_seq))
    )
    results = cursor.fetchall()
    existing = set([result[1] for result in results])
    to_insert = name_seq - existing
    print("seeding database")
    for name in to_insert:
        price = random.randint(int(message["minPrice"]), int(message["maxPrice"]))
        print("\t\tinserting entry with name <%s> and price <%d>" % (name, price))
        cursor.execute(
            "INSERT INTO demo (name, price) VALUES ('%s', %d)" % (name, price)
        )

    db.commit()
