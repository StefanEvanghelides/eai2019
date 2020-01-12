if (typeof WebSocket !== 'function') {
    Object.assign(global, { WebSocket: require('ws') });
}
const { Stomp } = require('@stomp/stompjs');
if (typeof TextEncoder !== 'function') {
    const {TextEncoder, TextDecoder} = require('text-encoding');
    Object.assign(global, { TextEncoder: TextEncoder });
    Object.assign(global, { TextDecoder: TextDecoder });
}

var url = "ws://localhost:61614";
var client = Stomp.client(url);

// Connect
var login = "admin";
var passcode = "admin";
//var header = {id: "store"};

var storeId = process.env.STORE_ID
var inputChannel = storeId + '-in'
var registryChannel = 'register-new-service'
var messageBusChannel = 'message-bus-in'

// var successCallback = function(message) {
//     if (message.body) {
//         console.log("Received message: " + message.body);
//     } else {
//         console.log("Received empty message");
//     }
// };

// var subscriptionCallback = function(frame) {
//     client.subscribe(replyDestination, successCallback)
//     console.log("Successfully subscribed");
        
//     // Send message
//     var requestDestination = "products";
//     var header = {};
//     var body = JSON.stringify({
//         type: "products",
//         action: "list",
//         page: 1,
//         pageSize: 5,
//         sender: "store"
//     });
//     client.send(requestDestination, header, body);
// };

function onMessage(message) {
    console.log("received a message!", message.body, message.headers)
    var headers = message.headers
    var body = JSON.parse(message.body)
    if(headers.type == 'response' && headers.subject == 'registration' && body.success) {
        var headers = {
            type: 'request',
            subject: 'products',
            sender: storeId,
            receiver: 'warehouse-message-handler'
        };
        var body = {
            action: "list",
            page: 1,
            pageSize: 5
        };
        client.send(
            messageBusChannel,
            headers,
            JSON.stringify(body)
        )
    }
}


function onConnect(frame) {
    client.subscribe(inputChannel, onMessage)
    var headers = {
        type: 'request',
        subject: 'registration',
        sender: storeId,
        receiver: 'message-bus'
    }

    var body = {
        'service-name': storeId,
        'input-channel': inputChannel
    }

    client.send(
        registryChannel,
        headers,
        JSON.stringify(body)
    )
}

document.getElementById('test-paragraph').innerHTML = `This store uses tax calculations from the ${process.env.LOCALE} locale`

function registerAtMessageBus(client) {
    client.connect(login, passcode, onConnect);
}

console.log(process.env, process.env.LOCALE)

registerAtMessageBus(client)