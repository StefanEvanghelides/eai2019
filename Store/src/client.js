if (typeof WebSocket !== 'function') {
    Object.assign(global, { WebSocket: require('ws') });
}
const { Stomp } = require('@stomp/stompjs');
if (typeof TextEncoder !== 'function') {
    const {TextEncoder, TextDecoder} = require('text-encoding');
    Object.assign(global, { TextEncoder: TextEncoder });
    Object.assign(global, { TextDecoder: TextDecoder });
}

var mainQueueUrl = "ws://localhost:62614";
var controlQueueUrl = "ws://localhost:62615";
var backupQueueUrl = "ws://localhost:62616";
var client = Stomp.client(mainQueueUrl);

var login = "admin";
var passcode = "admin";

var storeId = process.env.STORE_ID
var inputChannel = storeId + '-in'
var registryChannel = 'register-new-service'
var messageBusChannel = 'message-bus-in'

function onMessage(message) {
    console.log("received a message!", message.body, message.headers)
    var headers = message.headers
    var body = JSON.parse(message.body)
    if(headers.type == 'response' && headers.subject == 'registration' && body.success) {
        var headers = {
            type: 'request',
            subject: 'list-products',
            sender: storeId,
            receiver: 'warehouse-message-handler'
        };
        var body = {
            page: 1,
            pageSize: 5
        };
        client.send(
            messageBusChannel,
            headers,
            JSON.stringify(body)
        )
    } else if (headers.type == 'response' && headers.subject == 'list-products') {
        const products = body.products
        for(let product of products) {
            product_list = document.getElementById('product-list')
            current_html = product_list.innerHTML
            console.log(product)
            new_html = current_html + `<div>${product[1]} - ${product[3]} ${product[2]} - tax rate: ${product[4]}</div>`
            product_list.innerHTML = new_html
        }
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

function nextPage() {
    console.log("next page!")
}

function previousPage() {
    console.log("previousPage")
}

document.getElementById('test-paragraph').innerHTML = `This store uses tax calculations from the ${process.env.LOCALE} locale`

function registerAtMessageBus(client) {
    client.connect(login, passcode, onConnect);
}

console.log(process.env, process.env.LOCALE)

registerAtMessageBus(client)

document.getElementById('next-page').addEventListener("click", nextPage); 
document.getElementById('previous-page').addEventListener("click", previousPage); 