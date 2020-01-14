import stomp
import json


class MessageSender:
    def __init__(self, hosts, queue, *args, destination, **kwargs):
        super(MessageSender, self).__init__(*args, **kwargs)
        self.destination = destination
        self.queue = queue
        self.header_keys = ["type", "subject", "sender", "receiver"]

    def send(self, headers, message):
        self.queue.send(body=message, destination=self.destination, headers=headers)
        print("sent message %s to %s" % (message, self.destination))

    def send_registration_confirmation(self):
        headers = {
            "type": "response",
            "subject": "registration",
            "sender": "message-bus",
            "receiver": "warehouse-message-handler",
        }
        message = {"success": True}
        self.send(headers, json.dumps(message))
