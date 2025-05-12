class Seller:
    def __init__(self, name, phone_number, email, salary, seller_id):
        self.id = seller_id
        self.name = name
        self.phone_number = phone_number
        self.email = email
        self.salary = salary

    def to_dict(self):
        return vars(self) 