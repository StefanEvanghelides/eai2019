import json


def handle_product_translation(translators, message, headers, queues):
    message = json.loads(message)
    target_locale = message["locale"]
    translated = translators[target_locale].translate(message)
    print("translated message to %s" % target_locale)

    queues["message-bus"].send(
        body=json.dumps(translated), headers=headers, destination="message-bus-in"
    )
