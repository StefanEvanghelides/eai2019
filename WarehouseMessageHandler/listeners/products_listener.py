import stomp
import json
import math

class ProductsListener(stomp.ConnectionListener):
    def __init__(self, db, hosts, *args, **kwargs):
        super(ProductsListener, self).__init__(*args, **kwargs)
        self.db = db
        #self.hosts = hosts
        self.handlers_mapping = {
            'create': self.create,
            'delete': self.delete,
            'update': self.update,
            'list': self.list
        }
        self.queue = stomp.Connection(host_and_ports=hosts)
        self.queue.start()
        self.queue.connect('reply', 'reply', wait=True, headers = {'client-id': 'warehouse-listener'} )

    def on_error(self, headers, message):
        print('received an error "%s"' % message)

    def on_message(self, headers, message):
        print(message)
        parsed_message = json.loads(message)
        if parsed_message['type'] == 'products':
            handler = self.handlers_mapping[parsed_message['action']]
            handler(parsed_message)
            # cursor = db.cursor()
            # cursor.execute('SELECT * FROM demo')
            # products = cursor.fetchall()

            # queue = stomp.Connection(host_and_ports=self.hosts)
            # queue.start()
            # queue.connect('admin', 'admin', wait=True, headers = {'client-id': 'warehouse'} )
            # queue.send(body=json.dumps({'type': 'translate', 'products': products}), destination='Translate')
            # queue.disconnect()

        print('received a message "%s"' % message)


    def create(self, message):
        cursor = self.db.cursor()
        cursor.execute("INSERT INTO demo (name) VALUES ('%s')" % message['product-name'])
        print("Warehouse is inserting product with name %s" % message['product-name'])
        self.db.commit()

    def delete(self, message):
        cursor = self.db.cursor()
        cursor.execute("DELETE FROM demo WHERE id='%s'" % message[id])
        cursor.commit()

    def update(self, message):
        cursor = self.db.cursor()
        cursor.execute("UPDATE demo SET (name='%s') WHERE id='%s'" % (message['name'], message['id']))
        cursor.commit()

    def list(self, message):
        print("Warehouse received message: ", message)
        cursor = self.db.cursor()
        limit = message['pageSize']
        offset = max(0, message['page'] - 1) * limit
        cursor.execute("SELECT * FROM demo LIMIT %d OFFSET %d" % (limit, offset))
        result = cursor.fetchall()
        cursor.execute("SELECT COUNT(*) FROM demo")
        total_count = cursor.fetchall()[0][0]   # returns list of tuples for some reason
        print(offset, limit, total_count)
        has_next = offset + limit < total_count
        has_previous = offset > 0

        message = {
            'destination': 'store-1',
            'type': 'translate',
            'pageInfo': {
                'page': message['page'],
                'pageSize': message['pageSize'],
                'hasNextPage': has_next,
                'hasPreviousPage': has_previous,
                'pageCount': math.ceil(total_count / limit)
            },
            'products': result
        }

        self.queue.send(body=json.dumps(message), destination='reply')
        print("Warehouse sent products to reply channel", message)

