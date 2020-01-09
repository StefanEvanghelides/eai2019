Object.assign(global, { WebSocket: require('ws') });
var Stomp = require('@stomp/stompjs');

var url = "ws://localhost:61614";

var obj = {
    brokerURL: "ws://localhost:61614",
    connectHeaders: {
        login: "admin",
        passcode: "admin"
    }
};
var client = Stomp.Client(obj);

// Connect
var login = "admin";
var passcode = "admin";
var successCallback = function(message) {
    if (message.body) {
        alert("Received message: " + message.body);
    } else {
        alert("Received empty message");
    }
}
client.connect(login, passcode, successCallback);

// Send a message
destionation = "";
header = {};
body = "";
client.send(destination, header, body);
