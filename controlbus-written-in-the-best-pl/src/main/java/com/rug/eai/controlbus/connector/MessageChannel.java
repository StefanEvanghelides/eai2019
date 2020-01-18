package com.rug.eai.controlbus.connector;

import com.google.gson.Gson;
import org.springframework.jms.annotation.JmsListener;
import org.springframework.messaging.handler.annotation.SendTo;
import org.springframework.stereotype.Component;

import javax.jms.JMSException;

@Component
public class MessageChannel {

    private static final String REGISTRY = "registry";
    private static final String HEARTBEAT = "heartbeat";
    private static final String CHANNEL_OUT_OF_ORDER = "channel-out-of-order";

    @JmsListener(destination = "control-bus-in")
    public void receiveMessage(final String json) throws JMSException {
        System.out.println("Inside MessageChannel!");
        System.out.println("The message is " +  json);
        /*
        Message message = new Gson().fromJson(json, Message.class);
        System.out.println("Message header is " + message.getHeader());
        System.out.println("Message header sender is " + message.getHeader().getSender());
        System.out.println("Message header receiver is " + message.getHeader().getReceiver());
        System.out.println("Message header type is " + message.getHeader().getType());
        System.out.println("Message header subject is " + message.getHeader().getSubject());
        System.out.println("Message body is " + message.getBody());
        String subject = message.getHeader().getSubject();
        */
        triggerRerouting();
//        switch (subject) {
//            case REGISTRY:
//                System.out.println("Inside registry");
//                // TODO: add registration here
//                break;
//            case HEARTBEAT:
//                System.out.println("Inside Heartbeat");
//                // TODO: add hearbeat here
//                break;
//            case CHANNEL_OUT_OF_ORDER:
//                System.out.println("Inside COOO");
//                // TODO: add rerouting here
//                break;
//            default:
//                System.out.println("SUBJECT NOT SUPPORTED");
//        }
      


        /**
         *
         {
         header: {
         subject: channel-out-of-order,
         type: datagram,
         sender: service-name,
         receiver: control_bus
         },
         body: null
         }
         *
         "{
            \"name\": \"admin\"
         }"
         *
         {
         "headers" : {
            "subject": "channel-out-of-order",
            "type": "datagram",
            "sender": "<service-name>",
            "receiver": "control_bus"
         },

         "body": {
            "command": "channel-out-of-order"
         }
         }

         {
         "headers" : {
         "subject": "heart-beat",
         "type": "datagram",
         "sender": "<service-name>",
         "receiver": "control_bus"
         },

         "body": {
            "content": "heart-beat"
         }
         }
         */
    }


    public void triggerRerouting() {
        String message = "{" +
            "\"hostname\": \"backup-queue\"" +
            "}";
        rerouteWarehouseMessageHandler(message);
        rerouteWarehouseAdminInterface(message);
        rerouteTranslatorIn(message);
    }

    @SendTo("warehouse-message-handler-in")
    private String rerouteTranslatorIn(String message) {
        System.out.println("Send rerouting message to warehouse message handler");
        return message;
    }

    @SendTo("warehouse-admin-interface-in")
    private String rerouteWarehouseAdminInterface(String message) {
        System.out.println("Send rerouting message to admin interface");
        return message;
    }

    @SendTo("translator-in")
    private String rerouteWarehouseMessageHandler(String message) {
        System.out.println("Send rerouting message to translator");
        return message;
    }
}
