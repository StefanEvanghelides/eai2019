### Documentation

https://activemq.apache.org/rest


### Build app:
```
docker-compose build
```

### Run app:
```
docker-compose up
```

### Build and run:
```
docker-compose up --build
```

### Endpoints:
 - http://localhost:5000/products/new -> allows you to add products to the database
 - http://localhost/store-nl -> access NL Store (port 80)


### Build, run and scale:
```
docker-compose up --build --scale translator=3  --scale warehouse-message-handler=3 --scale warehouse-admin=3
```


### Services and channels [input-channel] -> service -> [output-channel]:
 - [message-bus-in] -> message-bus -> [ * ]
 - [warehouse-message-handler-in] -> warehouse-message-handler -> [message-bus-in]
 - [warehouse-admin-in] -> warehouse-admin -> [message-bus-in]
 - [store-nl-in] -> store-nl -> [message-bus-in]
 - [store-en-in] -> store-en -> [store-en-in]

### Message format examples:

#### Registration Request Message:
```
headers = {
    'type': 'request',
    'subject': 'registration',
    'sender': 'sending-service-id',
    'receiver': 'receiving-service-id'
}
body = {
    'service-name': 'sending-service-id,
    'input-channel': 'sending-service-input-channel'
}
```

#### Registration Response Message:
```
headers = {
    'type': 'response',
    'subject': 'registration',
    'sender': 'message-bus',
    'receiver': 'receiving-service-id'
}
body = {
    'success': True
}
```

#### Products Request:
```
headers = {
    'type': 'request',
    'subject': 'products',
    'sender': 'store-id',
    'receiver': 'warehouse-message-handler'
}
body = {
    'page': 1,
    'pageSize': 5,
    'action': "list",
}
```

#### Products Response:
```
headers = {
	'type': 'response',
	'subject': 'products',
	'sender': 'warehouse-message-handler',
	'receiver': store-id
}
body = {
    'pageInfo': {
        "page": 1,
        "pageSize": 5,
        "hasNextPage": True,
        "hasPreviousPage": False,
        "pageCount": 2,
    },
    'products': []
}
```

