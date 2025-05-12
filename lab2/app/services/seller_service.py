from app.models.seller import Seller

class SellerService:
    def __init__(self):
        self.sellers = []
        self.seller_id_counter = 1

    def get_all(self):
        return [seller.to_dict() for seller in self.sellers]

    def get_by_id(self, seller_id):
        return next((seller for seller in self.sellers if seller.id == seller_id), None)

    def create(self, data):
        new_seller = Seller(
            data['name'],
            data['phone_number'],
            data['email'],
            data['salary'],
            self.seller_id_counter
        )
        self.sellers.append(new_seller)
        self.seller_id_counter += 1
        return new_seller

    def update(self, seller_id, data):
        seller = self.get_by_id(seller_id)
        if seller:
            seller.name = data['name']
            seller.phone_number = data['phone_number']
            seller.email = data['email']
            seller.salary = data['salary']
        return seller

    def delete(self, seller_id):
        seller = self.get_by_id(seller_id)
        if seller:
            self.sellers.remove(seller)
        return seller 