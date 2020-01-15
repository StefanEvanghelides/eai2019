import time
from functools import partial
from Connection import Connection, Listener
from translators import Translator
from handlers.request_handlers import handle_product_translation

if __name__ == "__main__":
    translators = {
        "NL_EUR": Translator(1.0, 1.21, "€"),
        "GB_GBP": Translator(0.855, 1.2, "£"),
        "US_USD": Translator(1.11, 1.1, "$")
    }

    request_handlers = {
        "translate-products": partial(handle_product_translation, translators)
    }

    c = Connection(
        "main-queue",
        "control-queue",
        61613,
        Listener(request_handlers=request_handlers),
        "translator"
    )

    while True:
        # keep app running to prevent docker from terminating
        time.sleep(0.01)
