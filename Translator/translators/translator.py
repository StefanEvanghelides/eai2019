class Translator:
    def __init__(self, exchange_rate, vat_rate, currency_symbol, *args, **kwargs):
        super(Translator, self).__init__(*args, **kwargs)
        self.exchange_rate = exchange_rate
        self.vat_rate = vat_rate
        self.currency_symbol = currency_symbol
        tax_percent = round((float(vat_rate) - 1) * 100)
        self.tax_repr = str(tax_percent) + "%"

    def translate(self, message):
        products = message["products"]
        message["products"] = []
        for product in products:
            product[2] = round(
                product[2] * (self.vat_rate * self.exchange_rate) / 100, 2
            )
            product.append(self.currency_symbol)
            product.append(self.tax_repr)
            message["products"].append(product)
        return message
