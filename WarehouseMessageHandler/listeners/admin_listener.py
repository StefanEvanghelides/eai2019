import stomp
import json


class AdminListener(stomp.ConnectionListener):
    def __init__(self, db, hosts, *args, **kwargs):
        super(AdminListener, self).__init__(*args, **kwargs)
        self.db = db
        self.hosts = hosts
        self.handlers_mapping = {"create": self.create}

    def on_error(self, headers, message):
        print('received an error "%s"' % message)

    def on_message(self, headers, message):
        try:
            parsed_message = json.loads(message)
            if parsed_message["type"] == "products":
                handler = self.handlers_mapping[parsed_message["action"]]
                handler(parsed_message["content"])

            print('received a message "%s"' % message)
        except Exception as e:
            print("An error occured while receiving a message in the 'Admin' listener")
            traceback.print_exc()

    def create(self, message):
        cursor = self.db.cursor()
        cursor.execute(
            "INSERT INTO demo (name) VALUES ('%s')" % message["product-name"]
        )
        print("Warehouse is inserting product with name %s" % message["product-name"])
        self.db.commit()
