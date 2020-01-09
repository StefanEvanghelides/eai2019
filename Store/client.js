Object.assign(global, { WebSocket: require('ws') });
const { Stomp } = require('@stomp/stompjs');
if (typeof TextEncoder != 'function') {
    const {TextEncoder, TextDecoder} = require('text-encoding');
    Object.assign(global, { TextEncoder: TextEncoder });
    Object.assign(global, { TextDecoder: TextDecoder });
}

var url = "ws://localhost:61614";
var client = Stomp.client(url);

// Connect
var login = "admin";
var passcode = "admin";
var destination = "reply";
//var header = {id: "store"};
var successCallback = function(message) {
    if (message.body) {
        console.log("Received message: " + message.body);
    } else {
        console.log("Received empty message");
    }
};
var subscriptionCallback = function(frame) {
    console.log(client);
    client.subscribe(destination, successCallback)
    console.log("Successfully subscribed");
};

client.connect(login, passcode, subscriptionCallback);

