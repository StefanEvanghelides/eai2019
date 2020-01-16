import stomp
import json

# from ..router import MessageRouter


class MessageListener(stomp.ConnectionListener):
    def __init__(self, hosts, *args, **kwargs):
        super(MessageListener, self).__init__(*args, **kwargs)
        self.hosts = hosts
        # self.locale_mapping = {
        #     "store-nl": "NL_EUR",
        #     "store-gb": "GB_GBP",
        #     "store-us": "US_USD",
        # }

    def set_queue(self, queue):
        print("setting queue", queue)
        self.queue = queue

    def on_error(self, headers, message):
        print('received an error "%s"' % message)

    def on_message(self, headers, message):
        print("messagebus received a message", message, headers)
        print("queue", self.queue)
        self.queue.send(destination='warehouse-admin-interface-in', **{'type': "datagram", 'subject': 'set-message-queue'}, body=json.dumps({'host': 'backup-queue'}))
        self.queue.send(destination='translator-in', **{'type': "datagram", 'subject': 'set-message-queue'}, body=json.dumps({'host': 'backup-queue'}))
        self.queue.send(destination='warehouse-message-handler-in', **{'type': "datagram", 'subject': 'set-message-queue'}, body=json.dumps({'host': 'backup-queue'}))
        # parsed_message = json.loads(message) if message else ""

        # if (
        #     headers["type"] == "response"
        #     and headers["subject"] == "list-products"
        #     and not "correlation-id" in headers
        # ):
        #     # message must be translated first
        #     headers["correlation-id"] = "asdf123"
        #     headers["type"] = "request"
        #     parsed_message["locale"] = self.locale_mapping[headers["receiver"]]

        #     headers["subject"] = "translate-products"
        #     self.registry.send("translator", headers, json.dumps(parsed_message))
        # else:
        #     if headers["subject"] == "translate-products":
        #         # redirect translated message to store
        #         headers["subject"] = "list-products"
        #         headers["type"] = "response"
        #     self.registry.send(headers["receiver"], headers, message)
        # router = MessageRouter(destination=message['destination'])
        # router.send(message=message)
