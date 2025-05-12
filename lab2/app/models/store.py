class Store:
    def __init__(self, name, address, city, store_id):
        self.id = store_id
        self.name = name
        self.address = address
        self.city = city

    def to_dict(self):
        return vars(self) 