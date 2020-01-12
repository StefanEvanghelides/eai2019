import stomp
import json
# from ..router import MessageRouter



class MessageListener(stomp.ConnectionListener):
    def __init__(self, hosts, registry, *args, **kwargs):
        super(MessageListener, self).__init__(*args, **kwargs)
        self.hosts = hosts
        self.registry = registry
        
    def on_error(self, headers, message):
        print('received an error "%s"' % message)

    def on_message(self, headers, message):
        print('messagebus received a message', message, headers)
        parsed_message = json.loads(message)
        self.registry.send(headers['receiver'], headers, message)
        # router = MessageRouter(destination=message['destination'])
        # router.send(message=message)
