import stomp

class ProductsListener(stomp.ConnectionListener):
    def __init__(self, db, hosts, *args, **kwargs):
        super(ProductsListener, self).__init__(*args, **kwargs)
        self.db = db
        self.hosts = hosts

    def on_error(self, headers, message):
        print('received an error "%s"' % message)

    def on_message(self, headers, message):
        parsed_message = json.loads(message)
        if parsed_message['type'] == 'products':
            cursor = db.cursor()
            cursor.execute('SELECT * FROM demo')
            products = cursor.fetchall()

            queue = stomp.Connection(host_and_ports=self.hosts)
            queue.start()
            queue.connect('admin', 'admin', wait=True, headers = {'client-id': 'warehouse'} )
            queue.send(body=json.dumps({'type': 'translate', 'products': products}), destination='Translate')
            queue.disconnect()

        print('received a message "%s"' % message)

