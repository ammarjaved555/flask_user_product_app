from flask import Blueprint, request, jsonify
from models.order import Order
from models.product import Product
from models.user import User
from models import db
from services.auth import token_required
from sqlalchemy.exc import IntegrityError

order_blueprint = Blueprint('order_blueprint', __name__)

@order_blueprint.route('/', methods=['GET'])
@token_required
def get_orders(current_user):
    try:
        orders = Order.query.filter_by(user_id=current_user.id).all()
        orders_list = [{
            'id': order.id,
            'product_id': order.product_id,
            'user_id': order.user_id,
            'quantity': order.quantity,
            'status': order.status,
            'date_created': order.date_created.isoformat()
        } for order in orders]
        return jsonify(orders_list)
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@order_blueprint.route('/add', methods=['POST'])
@token_required
def add_orders(current_user):
    try:
        data = request.get_json()
        if not data or not isinstance(data, list):
            return jsonify({'message': 'Request body must be a list of orders'}), 400

        orders = []
        for order_data in data:
            if not {'product_id', 'quantity'}.issubset(order_data):
                return jsonify({'message': 'Missing required fields in one of the orders'}), 400

            product = Product.query.get(order_data['product_id'])
            if not product:
                return jsonify({'message': f"Product with id {order_data['product_id']} not found"}), 404

            order = Order(
                product_id=order_data['product_id'],
                user_id=current_user.id,
                quantity=order_data['quantity'],
                status='Pending'
            )
            orders.append(order)

        db.session.add_all(orders)
        db.session.commit()

        return jsonify({'message': 'Orders placed successfully'}), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({'message': 'Database error occurred. Please try again.'}), 500

    except Exception as e:
        return jsonify({'message': str(e)}), 500


@order_blueprint.route('/my_orders', methods=['GET'])
@token_required
def get_user_orders(current_user):
    try:
        orders = Order.query.filter_by(user_id=current_user.id).all()
        if not orders:
            return jsonify({'message': 'No orders found'}), 404

        orders_list = [{
            'id': order.id,
            'product_id': order.product_id,
            'user_id': order.user_id,
            'quantity': order.quantity,
            'status': order.status,
            'date_created': order.date_created.isoformat()
        } for order in orders]

        return jsonify(orders_list), 200

    except Exception as e:
        return jsonify({'message': str(e)}), 500


