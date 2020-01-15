import stomp
import json

from .sender import MessageSender


"""
message format:

{
    headers: {
        type: 'request' || 'reply',
        from: 'sender-channel',
        to: 'receiver-channel'
    },
    body: {
        ...
    }
}

    
"""


class ServiceRegistrationListener(stomp.ConnectionListener):
    def __init__(self, hosts, *args, **kwargs):
        super(ServiceRegistrationListener, self).__init__(*args, **kwargs)
        self.hosts = hosts
        self.registered_services = {}

    def on_error(self, headers, message):
        print("error", headers)

    def on_message(self, headers, message):
        message = json.loads(message)
        service = message["service-name"]
        return_channel = message["input-channel"]

        # if not service in self.registered_services:
        if not service in self.registered_services:
            queue = stomp.Connection(host_and_ports=self.hosts)
            queue.start()
            queue.connect(
                "admin",
                "admin",
                wait=True,
                headers={"client-id": "message-bus-sender-%s" % service},
            )
            self.registered_services[service] = MessageSender(
                self.hosts, queue, destination=return_channel
            )
            print("Registry sucesfully registered service <%s>" % service)
        self.registered_services[service].send_registration_confirmation()

        # print("registration listener received message:", headers, message)
        # service = message['service']
        # if not service in self.registered_services:
        #     self.registered_services['service'] = MessageSender(self.hosts, destination=service)
        #     print("created new message sender for service %s" % service)

    def send(self, destination, headers, message):
        self.registered_services[destination].send(headers, message)
