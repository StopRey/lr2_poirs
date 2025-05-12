from flask import Blueprint, request, jsonify
from app.services.product_service import ProductService

product_bp = Blueprint('products', __name__)
product_service = ProductService()

class ProductController:
    @product_bp.route('/products', methods=['GET', 'POST'])
    def manage_products():
        if request.method == 'GET':
            return jsonify(product_service.get_all()), 200
        elif request.method == 'POST':
            data = request.get_json()
            new_product = product_service.create(data)
            return jsonify(new_product.to_dict()), 201

    @product_bp.route('/products/<int:id>', methods=['GET', 'PUT', 'DELETE'])
    def handle_product(id):
        product = product_service.get_by_id(id)
        if not product:
            return jsonify({"message": "Product not found"}), 404

        if request.method == 'GET':
            return jsonify(product.to_dict()), 200
        elif request.method == 'PUT':
            data = request.get_json()
            updated_product = product_service.update(id, data)
            return jsonify(updated_product.to_dict()), 200
        elif request.method == 'DELETE':
            deleted_product = product_service.delete(id)
            return jsonify(deleted_product.to_dict()), 200 