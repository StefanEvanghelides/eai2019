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


### Services and channels [input-channel] -> service -> [output-channel]:
 - [message-bus-in] -> message-bus -> [ * ]
 - [warehouse-message-handler-in] -> warehouse-message-handler -> [message-bus-in]
 - [warehouse-admin-in] -> warehouse-admin -> [message-bus-in]
 - [store-nl-in] -> store-nl -> [message-bus-in]
 - [store-en-in] -> store-en -> [store-en-in]
