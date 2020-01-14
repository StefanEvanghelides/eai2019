import stomp
import json
from datetime import datetime
import traceback
import time

class Listener(stomp.ConnectionListener):
    def __init__(self, request_handlers={}, response_handlers={}, *args, **kwargs):
        super(Listener, self).__init__(*args, **kwargs)
        self.queues = {}
        self.request_handlers = request_handlers
        self.response_handlers = response_handlers
        self.request_handlers['set-message-queue'] = self.handle_set_message_bus
        self.response_handlers['registration'] = self.start_heart_beat

    def on_message(self, headers, message):
        
        print("RECEIVED MESSAGE!", message, headers)
        print(self.response_handlers)
        try:
            if headers['type'] == 'request':
                self.request_handlers[headers['subject']](message, headers, self.queues)
            else:
                self.response_handlers[headers['subject']](message, headers, self.queues)
        except Exception as e:
            print(e)
            traceback.print_exc()
            print("No such %s handler: %s" % (headers['type'], headers['subject']))

    def handle_set_message_bus(self, message, headers):
        self.conn.set_message_bus(message['host'], message['port'])

    def start_heart_beat(self, message, headers, queues):
        while True:
            body = {
                'heartbeat': datetime.now()
            }
            headers = {
                'type': 'other',
                'subject': 'heartbeat',
                'sender': self.conn.service_name,
                'receiver': 'message-bus'
            }
            queues['message-bus'].send(
                body=json.dumps(message),
                **headers,
                destination='message-bus-in'
            )
            print("Sent heartbeat to message bus; sleeping for 5 seconds")
            time.sleep(5)

    def set_queue(self, key, queue):
        self.queues[key] = queue

    def set_connection(self, conn):
        self.conn = conn