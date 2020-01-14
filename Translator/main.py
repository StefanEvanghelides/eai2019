import psycopg2
import time
import os
import sys
import stomp
from urllib import request, parse, error
import json
import math
import traceback


class EuroTranslator():
    def translate(self, message):
        exchange_rate = 1.0
        vat_rate = 1.21
        products = message['products']
        message['products'] = []
        for product in products:
            product[2] *= vat_rate * exchange_rate
            product.append('€')
            product.append('21%')
            message['products'].append(product)
        return message

class PoundTranslator():
    def translate(self, message):
        exchange_rate = 0.855
        vat_rate = 1.2
        products = message['products']
        message['products'] = []
        for product in products:
            product[2] *= vat_rate * exchange_rate
            product.append('£')
            product.append('20%')
            message['products'].append(product)
        return message

class DollarTranslator():
    def translate(self, message):
        exchange_rate = 1.11
        vat_rate = 1.1
        products = message['products']
        message['products'] = [] 
        for product in products:
            product[2] *= vat_rate * exchange_rate
            product.append('$')
            product.append('10%')
            message['products'].append(product)
        return message


class MessageListener(stomp.ConnectionListener):
    def __init__(self, db, hosts, queue, *args, **kwargs):
        super(MessageListener, self).__init__(*args, **kwargs)
        # self.hosts = hosts
        self.db = db
        self.queue = queue
        self.handlers_mapping = {
            "products": self.handle_product_translation,
            'registration': self.handle_registration_confirmation
        }
        self.translators = {
            'NL_EUR': EuroTranslator(),
            'GB_GBP': PoundTranslator(),
            'US_USD': DollarTranslator()
        }

    def on_error(self, headers, message):
        print('received an error "%s"' % message)

    def on_message(self, headers, message):
        try:
            print("MESSAGE IN %s" % os.environ['HOSTNAME'])
            parsed_message = json.loads(message)

            handler = self.handlers_mapping[headers["subject"]]
            handler(headers, parsed_message)

            print('Warehouse products listener received a message "%s"' % message)
        except Exception as e:
            print(
                "An error occured while receiving a message in the 'Products' listener"
            )
            traceback.print_exc()

    def handle_product_translation(self, headers, message):
        target_locale = message['locale']
        translated = self.translators[target_locale].translate(message)
        print("translated message to %s" % target_locale)

        self.queue.send(
            body=json.dumps(translated),
            headers=headers,
            destination='message-bus-in'
        )

    def handle_registration_confirmation(self, headers, message):
        print("sucesfully received registration confirmation from message-bus")




def start_message_listener(conn, hosts, send_queue):
    print("starting listener for administrator channel")
    queue = stomp.Connection(host_and_ports=hosts)
    queue.set_listener("", MessageListener(conn, hosts, send_queue))
    queue.start()
    queue.connect("admin", "admin", wait=True, headers={"client-id": os.environ['HOSTNAME'] + '-listener'})
    queue.subscribe(
        destination="translator-in",
        id=1,
        ack="auto",
        headers={
            "subscription-type": "MULTICAST",
            "durable-subscription-name": "someValue",
        },
    )

    print("sucesfully subscribed to 'warehouse-message-in' channel")

def register_at_message_bus(hosts, queue):
    headers = {
        'type': 'request',
        'subject': 'registration',
        'sender': 'translator',
        'receiver': 'message-bus'
    }
    body = {
        'service-name': 'translator',
        'input-channel': 'translator-in'
    }
    queue.send(
        body=json.dumps(body),
        **headers,
        destination="register-new-service"
    )

    print("send registration request to message bus")


if __name__ == "__main__":
    time.sleep(10)
    hosts = [("queue", 61613)]
    conn = psycopg2.connect(host="postgres", port=5432, user="postgres")
    queue = stomp.Connection(host_and_ports=hosts)
    queue.start()
    queue.connect("admin", "admin", wait=True, headers={"client-id": os.environ['HOSTNAME']})
    register_at_message_bus(hosts, queue)
    start_message_listener(conn, hosts, queue)

    while True:
        # keep app running to prevent docker from terminating
        time.sleep(0.01)
