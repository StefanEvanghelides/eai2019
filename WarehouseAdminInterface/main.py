import psycopg2
import time
import os
import sys
import stomp
from urllib import request, parse, error
import json
from flask import (
    Flask,
    request,
    render_template,
    redirect,
    send_from_directory
)
import random
app = Flask(__name__)
env_vars = dict(os.environ)
conn = psycopg2.connect(host='postgres', port=5432, user='postgres')

# class MyListener(stomp.ConnectionListener):
#         def on_error(self, headers, message):
#             print('received an error "%s"' % message)
#         def on_message(self, headers, message):
#             print('received a message "%s"' % message)
# hosts = [('queue', 61613)]

# time.sleep(3)


def create_demo_table(conn):
    print("creating demo table")
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS demo')
    cursor.execute('CREATE TABLE IF NOT EXISTS demo (id SERIAL, name VARCHAR(64), price INTEGER)')
    conn.commit()

def seed_db(conn):
    cursor = conn.cursor()
    
    name_seq = set(['test entry %d' % i for i in range(10)])

    cursor.execute("SELECT * FROM demo WHERE name IN (%s)" % ', '.join(map(lambda item: '\'%s\'' % item, name_seq)))
    results = cursor.fetchall()
    existing = set([result[1] for result in results])
    to_insert = name_seq - existing
    print("seeding database")
    for name in to_insert:
        price = random.randint(1000, 10000)
        print("\t\tinserting entry with name <%s> and price <%d>" % (name, price))
        cursor.execute("INSERT INTO demo (name, price) VALUES ('%s', %d)" % (name, price))

    conn.commit()

@app.route('/products/new', methods=['POST', 'GET'])
def new_product():

    app.logger.info('Create new product')
    if request.method == 'GET':
        entries = []
        return render_template('product_form.html')
    else:
        cursor = conn.cursor()
        product_name = request.form.get('product-name')
        product_price = request.form.get('product-price')
        if not product_name or not product_price:
            return render_template('product_form.html', error=True, message='Product name or price is missing')
        
        hosts = [('queue', 61613)]
        queue = stomp.Connection(host_and_ports=hosts)
        queue.start()
        queue.connect('admin', 'admin', wait=True, headers = {'client-id': 'warehouse-admin'} )
        message = json.dumps({'type': 'products', 'action': 'create', 'content': {'product-name': product_name, 'price': product_price}})
        queue.send(body=message, destination='admin')
        queue.disconnect()
        app.logger.info('sent message')
        return render_template('product_form.html', succes=True, product_name=product_name)


@app.route('/products/list', methods=['GET'])
def list_product():
    hosts = [('queue', 61613)]
    queue = stomp.Connection(host_and_ports=hosts)
    queue.start()
    queue.connect('products', 'products', wait=True, headers = {'client-id': 'warehouse-product-list'} )
    message = json.dumps({'type': 'products', 'action': 'list', 'page': 1, 'pageSize': 5})
    queue.send(body=message, destination='products')
    queue.disconnect()
    return render_template("request_list.html", success=True, message="requests product list")


if __name__ == '__main__':
    print("hello!")
    time.sleep(2)
    create_demo_table(conn)
    seed_db(conn)


    app.run(debug=True, host='0.0.0.0', use_reloader=False)

        # queue2 = stomp.Connection(host_and_ports=hosts)
        # queue2.start()
        # queue2.connect('admin', 'admin', wait=True, headers = {'client-id': 'warehouse-products'} )
        # queue2.send(body=json.dumps({'type': 'products'}), destination='ProductRequests')
        # queue2.disconnect()

    # urllib.urlopen('http://admin:admin@queue:8161/api/message?destination=queue://orders.input', {'body': 'test123'}) 
    # import stomp




    # time.sleep(3)
    # import requests
    # resp = requests.post('http://queue:8161/api/message?destination=topic://orders.input', data={'body': 'test123'}, auth=('admin', 'admin'))
    # print(resp)
    # print(resp.content)

    # time.sleep(2)
    # resp = requests.get('http://queue:8161/api/message?destination=topic://orders.input&clientId=warehouse&oneShot=true', auth=('admin', 'admin'))
    # print(resp)
    # print(resp.content)
    # proxy = req.ProxyHandler({'http': r'http://admin:admin@queue:8161'})
    # auth = req.HTTPBasicAuthHandler()
    # opener = req.build_opener(proxy, auth, req.HTTPHandler)
    # req.install_opener(opener)
    # conn = req.urlopen('http://admin:admin@queue:8161/api/message?destination=queue://orders.input')
    # return_str = conn.read()


 #    address = 'http://admin:admin@queue:8161/api/message?destination=queue://orders.input'

 #    req = request.Request(
 #        address,
 #        method="POST",
 #        data=parse.urlencode({'body': 'test123'}).encode("utf-8")
 #    )

 #    resp = request.urlopen(req)
 #    if not resp.getcode() == 200:
 #        print("ERR")
 #    else:
 #        print("SUCCES!")

 #    req = request.Request(
 #        address,
 #        method="GET"
 #    )

    # resp = request.urlopen(req)
    # print(resp)
    # cursor = conn.cursor()
    
    # print("creating demo table")
    # cursor.execute('CREATE TABLE IF NOT EXISTS demo (id SERIAL, name VARCHAR(64))')
    # print("inserting demo entry into demo table")
    # cursor.execute("INSERT INTO demo (name) VALUES ('test entry')")
    # cursor.execute("INSERT INTO demo (name) VALUES ('test entry2')")
    # print("querying demo table")
    # cursor.execute("SELECT * FROM demo")
    # result = cursor.fetchall()
    # conn.commit()
    # print(result)
    # conn.close()


    # time.sleep(5)

    # print("hello!")
    # conn = psycopg2.connect(host='postgres', port=5432, user='postgres')
    # cursor = conn.cursor()
    # print(conn)
    # print(cursor)
    # # print("dropping existing table")
    # # cursor.execute('DROP TABLE IF EXISTS demo')
    # print("creating demo table")
    # cursor.execute('CREATE TABLE IF NOT EXISTS demo (id SERIAL, name VARCHAR(64))')
    # print("inserting demo entry into demo table")
    # cursor.execute("INSERT INTO demo (name) VALUES ('test entry')")
    # print("querying demo table")
    # cursor.execute("SELECT * FROM demo")
    # result = cursor.fetchall()
    # print(result)
    # conn.close()