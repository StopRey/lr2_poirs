from flask import Blueprint, request, jsonify
from app.services.seller_service import SellerService

seller_bp = Blueprint('sellers', __name__)
seller_service = SellerService()

class SellerController:
    @seller_bp.route('/sellers', methods=['GET', 'POST'])
    def manage_sellers():
        if request.method == 'GET':
            return jsonify(seller_service.get_all()), 200
        elif request.method == 'POST':
            data = request.get_json()
            new_seller = seller_service.create(data)
            return jsonify(new_seller.to_dict()), 201

    @seller_bp.route('/sellers/<int:id>', methods=['GET', 'PUT', 'DELETE'])
    def handle_seller(id):
        seller = seller_service.get_by_id(id)
        if not seller:
            return jsonify({"message": "Seller not found"}), 404

        if request.method == 'GET':
            return jsonify(seller.to_dict()), 200
        elif request.method == 'PUT':
            data = request.get_json()
            updated_seller = seller_service.update(id, data)
            return jsonify(updated_seller.to_dict()), 200
        elif request.method == 'DELETE':
            deleted_seller = seller_service.delete(id)
            return jsonify(deleted_seller.to_dict()), 200 