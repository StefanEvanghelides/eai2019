import stomp
import json
# from ..router import MessageRouter



class MessageListener(stomp.ConnectionListener):
    def __init__(self, hosts, registry, *args, **kwargs):
        super(MessageListener, self).__init__(*args, **kwargs)
        self.hosts = hosts
        self.registry = registry
        self.locale_mapping = {
        	'store-nl': 'NL_EUR',
        	'store-gb': 'GB_GBP',
        	'store-us': 'US_USD'
        }

        
    def on_error(self, headers, message):
        print('received an error "%s"' % message)

    def on_message(self, headers, message):
        print('messagebus received a message', message, headers)
        parsed_message = json.loads(message) if message else ''

        if headers['type'] == 'response' and headers['subject'] == 'products' and not 'correlation-id' in headers:
        	# message must be translated first
        	headers['correlation-id'] = 'asdf123'
        	parsed_message['locale'] = self.locale_mapping[headers['receiver']]

        	self.registry.send('translator', headers, json.dumps(parsed_message))
        else:
        	self.registry.send(headers['receiver'], headers, message)
        # router = MessageRouter(destination=message['destination'])
        # router.send(message=message)
