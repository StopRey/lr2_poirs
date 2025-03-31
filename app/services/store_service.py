from app.models.store import Store

class StoreService:
    def __init__(self):
        self.stores = []
        self.store_id_counter = 1

    def get_all(self):
        return [store.to_dict() for store in self.stores]

    def get_by_id(self, store_id):
        return next((store for store in self.stores if store.id == store_id), None)

    def create(self, data):
        new_store = Store(
            data['name'],
            data['address'],
            data['city'],
            self.store_id_counter
        )
        self.stores.append(new_store)
        self.store_id_counter += 1
        return new_store

    def update(self, store_id, data):
        store = self.get_by_id(store_id)
        if store:
            store.name = data['name']
            store.address = data['address']
            store.city = data['city']
        return store

    def delete(self, store_id):
        store = self.get_by_id(store_id)
        if store:
            self.stores.remove(store)
        return store 