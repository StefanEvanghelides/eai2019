import stomp
import os
import time
import json


class Connection:
    def __init__(
        self, message_bus, control_bus, port, listener, service_name, *args, **kwargs
    ):
        super(Connection, self).__init__(*args, **kwargs)
        self.port = port
        self.service_name = service_name
        self.listener = listener
        self.message_bus = self.connect_to_queue(message_bus, self.port, listener)
        self.control_bus = self.connect_to_queue(control_bus, self.port, listener)
        self.listener.set_queue("message-bus", self.message_bus)
        self.listener.set_connection(self)
        self.listener.set_queue('control-bus', self.control_bus)

        self.register_at_message_bus()
        # self.register_at_control_bus()

    def register_at_message_bus(self):
        self.message_bus.subscribe(
            destination=self.service_name + "-in",
            id=1,
            ack="auto",
            headers={
                "subscription-type": "MULTICAST",
                "durable-subscription-name": "someValue",
            },
        )
        headers = {
            "type": "request",
            "subject": "registration",
            "sender": self.service_name,
            "receiver": "message-bus",
        }
        body = {
            "service-name": self.service_name,
            "input-channel": self.service_name + "-in",
        }
        self.message_bus.send(
            body=json.dumps(body), **headers, destination="register-new-service"
        )

    def send(self, queue, headers, body):
        if queue == 'message-bus':
            self.message_bus.send(body=json.dumps(body), **headers, destination='message-bus-in')
        elif queue == 'control-bus':
            pass
            # self.control_bus.send(body=json.dumps(body), **headers, destination='control-bus-in')
        else:
            print("No such queue: %s" % queue)

    def register_at_control_bus(self):
        pass

    def set_message_bus(self, host, port):
        if self.message_bus:
            # stop connection
            pass
        self.message_bus = self.connect_to_queue(host, port, self.listener)
        self.listener.set_queue("message-bus", self.message_bus)

    def connect_to_queue(self, host, port, listener):
        conn = stomp.Connection(host_and_ports=[(host, port)])
        conn.start()
        i = 0
        while i < 3:
            try:
                conn.connect(
                    "admin",
                    "admin",
                    wait=True,
                    headers={"client-id": os.environ["HOSTNAME"]},
                )
                break
            except Exception:
                print(
                    "connection to %s:%d failed. Retrying in 5 seconds" % (host, port)
                )
                time.sleep(5)
            i += 1
        conn.set_listener("", listener)
        return conn
