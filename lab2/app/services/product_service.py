from app.models.product import Product

class ProductService:
    def __init__(self):
        self.products = []
        self.product_id_counter = 1

    def get_all(self):
        return [product.to_dict() for product in self.products]

    def get_by_id(self, product_id):
        return next((prod for prod in self.products if prod.id == product_id), None)

    def create(self, data):
        new_product = Product(
            data['name'],
            data['price'],
            data['weight'],
            self.product_id_counter
        )
        self.products.append(new_product)
        self.product_id_counter += 1
        return new_product

    def update(self, product_id, data):
        product = self.get_by_id(product_id)
        if product:
            product.name = data['name']
            product.price = data['price']
            product.weight = data['weight']
        return product

    def delete(self, product_id):
        product = self.get_by_id(product_id)
        if product:
            self.products.remove(product)
        return product 