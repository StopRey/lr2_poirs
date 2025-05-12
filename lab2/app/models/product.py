class Product:
    def __init__(self, name, price, weight, product_id):
        self.id = product_id
        self.name = name
        self.price = price
        self.weight = weight

    def to_dict(self):
        return vars(self) 