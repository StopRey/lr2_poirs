from flask import Blueprint, request, jsonify
from app.services.store_service import StoreService

store_bp = Blueprint('stores', __name__)
store_service = StoreService()

class StoreController:
    @store_bp.route('/stores', methods=['GET', 'POST'])
    def manage_stores():
        if request.method == 'GET':
            return jsonify(store_service.get_all()), 200
        elif request.method == 'POST':
            data = request.get_json()
            new_store = store_service.create(data)
            return jsonify(new_store.to_dict()), 201

    @store_bp.route('/stores/<int:id>', methods=['GET', 'PUT', 'DELETE'])
    def handle_store(id):
        store = store_service.get_by_id(id)
        if not store:
            return jsonify({"message": "Store not found"}), 404

        if request.method == 'GET':
            return jsonify(store.to_dict()), 200
        elif request.method == 'PUT':
            data = request.get_json()
            updated_store = store_service.update(id, data)
            return jsonify(updated_store.to_dict()), 200
        elif request.method == 'DELETE':
            deleted_store = store_service.delete(id)
            return jsonify(deleted_store.to_dict()), 200 