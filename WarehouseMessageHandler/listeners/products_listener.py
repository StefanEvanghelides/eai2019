import stomp
import json
import math

class ProductsListener(stomp.ConnectionListener):
    def __init__(self, db, hosts, *args, **kwargs):
        super(ProductsListener, self).__init__(*args, **kwargs)
        self.db = db
        #self.hosts = hosts
        self.handlers_mapping = {
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

        print('Warehouse products listener received a message "%s"' % message)


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

