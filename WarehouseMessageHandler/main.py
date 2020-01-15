import psycopg2
import time

from Connection import Connection, Listener
from functools import partial
from handlers.request_handlers import list_products, create_product, create_db, seed_db

if __name__ == "__main__":
    conn = psycopg2.connect(host="postgres", port=5432, user="postgres")
    request_handlers = {
        "list-products": partial(list_products, conn),
        "create-product": partial(create_product, conn),
        "create-database": partial(create_db, conn),
        "seed-database": partial(seed_db, conn),
    }
    c = Connection(
        "queue",
        "queue",
        61613,
        Listener(request_handlers=request_handlers),
        "warehouse-message-handler",
    )

    while True:
        # keep app running to prevent docker from terminating
        time.sleep(0.01)
