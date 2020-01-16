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

var page = 1
var pageSize = 10
var maxPage = 1



function requestPage() {
    var headers = {
        type: 'request',
        subject: 'list-products',
        sender: storeId,
        receiver: 'warehouse-message-handler'
    };
    var body = {
        page: page,
        pageSize: pageSize
    };
    client.send(
        messageBusChannel,
        headers,
        JSON.stringify(body)
    )
}

function onMessage(message) {
    console.log("received a message!", message.body, message.headers)
    var headers = message.headers
    var body = JSON.parse(message.body)
    if(headers.type == 'response' && headers.subject == 'registration' && body.success) {
        requestPage()
    } else if (headers.type == 'response' && headers.subject == 'list-products') {
        const products = body.products
        maxPage = body.pageInfo.pageCount
        product_list = document.getElementById('product-list')
        product_list.innerHTML = ""
        for(let product of products) {
            current_html = product_list.innerHTML
            console.log(product)
            new_html = current_html + `<div style="font-size: 30px">${product[1]} - ${product[3]} ${product[2]} - tax rate: ${product[4]}</div>`
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
    page += 1;
    if(page >= maxPage) {
        page = maxPage
        document.getElementById('next-page').disabled=true
    }
    requestPage()
    document.getElementById('previous-page').disabled=false
}

function previousPage() {
    console.log("previousPage")
    page -= 1;
    if(page <= 1) {
        page = 1
        document.getElementById('previous-page').disabled=true
    }
    requestPage()
    document.getElementById('next-page').disabled=false
}

document.getElementById('test-paragraph').innerHTML = `This store uses tax calculations from the ${process.env.LOCALE} locale`

function registerAtMessageBus(client) {
    client.connect(login, passcode, onConnect);
}

console.log(process.env, process.env.LOCALE)

registerAtMessageBus(client)

document.getElementById('next-page').addEventListener("click", nextPage); 
document.getElementById('previous-page').addEventListener("click", previousPage); 