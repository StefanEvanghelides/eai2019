package com.rug.eai.controlbus.connector;

import com.google.gson.Gson;
import org.springframework.jms.annotation.JmsListener;
import org.springframework.stereotype.Component;

import javax.jms.JMSException;

@Component
public class MessageChannel {

    @JmsListener(destination = "control-bus-in")
    public void receiveMessage(final String json) throws JMSException {
        System.out.println("Inside MessageChannel!");
        System.out.println("The message is " +  json);
        Message message = new Gson().fromJson(json, Message.class);
        System.out.println("Message name is " + message.getName());
        //TODO: spit heartbeat and channel not available messages
    }
}
