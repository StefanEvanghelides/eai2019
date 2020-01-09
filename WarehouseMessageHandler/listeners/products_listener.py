import stomp

class ProductsListener(stomp.ConnectionListener):
    def __init__(self, db, hosts, *args, **kwargs):
        super(ProductsListener, self).__init__(*args, **kwargs)
        self.db = db
        self.hosts = hosts
        self.handlers_mapping = {
            'create': self.create,
            'delete': self.delete,
            'update': self.update,
            'list': self.list
        }

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
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM demo LIMIT %d OFFSET %d" % (5, 5*(message['page']-1)))
        result = cursor.fetchall()
        print(result)

