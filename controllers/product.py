from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from models.product import Product
from models import db

product_blueprint = Blueprint('product_blueprint', __name__)

@product_blueprint.route('/', methods=['GET'])
def get_products():
    try:
        products = Product.query.all()
        products_list = [{
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'price': product.price,
            'date_added': product.date_added.isoformat()
        } for product in products]
        return jsonify(products_list)
    except Exception as e:
        return jsonify({'message': str(e)}), 500
    
@product_blueprint.route('/add', methods=['POST'])
def add_product():
    try:
        data = request.get_json()
        if not data or not {'name', 'description', 'price'}.issubset(data):
            return jsonify({'message': 'Missing required fields'}), 400

        product = Product(name=data['name'], description=data['description'], price=data['price'])
        db.session.add(product)
        db.session.commit()

        return jsonify({'message': 'Product added successfully'}), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({'message': 'Database error occurred. Please try again.'}), 500

    except Exception as e:
        return jsonify({'message': str(e)}), 500