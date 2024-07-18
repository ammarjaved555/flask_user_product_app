from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from functools import wraps
from models import db
from models.user import User
from services.auth import generate_access_token, generate_refresh_token, verify_token
from flask_bcrypt import Bcrypt

user_blueprint = Blueprint('user_blueprint', __name__)
bcrypt = Bcrypt()

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
       
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]  
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            user_id = verify_token(token)
            if not user_id:
                return jsonify({'message': 'Token is invalid or expired!'}), 401
            current_user = User.query.get(user_id)
            if not current_user:
                return jsonify({'message': 'User not found!'}), 404
        except Exception as e:
            return jsonify({'message': 'Something went wrong: ' + str(e)}), 500
        
        return f(current_user, *args, **kwargs)
    
    return decorated

@user_blueprint.route('/', methods=['GET'])
def get_users():
    try:
        users = User.query.all()
        users_list = [ {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'password': user.password,
                'confirm_password': user.confirm_password,
                'date_created': user.date_created.isoformat()
            } for user in users]
        return jsonify(users_list)
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@user_blueprint.route('/register', methods=['POST'])
def register():
    print("register")
    try:
        data = request.get_json()
        if not data or not {'username', 'email', 'password', 'confirm_password'}.issubset(data):
            return jsonify({'message': 'Missing required fields'}), 400

        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({'message': 'Email already registered. Please try with different email.'}), 400

        if data['password'] != data.get('confirm_password'):
            return jsonify({'message': 'Passwords do not match'}), 400

        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        user = User(username=data['username'], email=data['email'], password=hashed_password, confirm_password=hashed_password)
        db.session.add(user)
        db.session.commit()
        access_token = generate_access_token(user)
        refresh_token = generate_refresh_token(user)

        return jsonify({'message': 'User created successfully', 'access_token': access_token, 'refresh_token': refresh_token}), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({'message': 'Database error occurred. Please try again.'}), 500

    except Exception as e:
        return jsonify({'message': str(e)}), 500

@user_blueprint.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data or not {'email', 'password'}.issubset(data):
            return jsonify({'message': 'Missing email or password'}), 400

        user = User.query.filter_by(email=data['email']).first()
        if user and bcrypt.check_password_hash(user.password, data['password']):
            access_token = generate_access_token(user)
            refresh_token = generate_refresh_token(user)
            return jsonify({'message': 'Login successful', 'access_token': access_token, 'refresh_token': refresh_token,'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'date_created': user.date_created.isoformat()
            }}), 200
        else:
            return jsonify({'message': 'Invalid email or password'}), 401

    except Exception as e:
        return jsonify({'message': str(e)}), 500

@user_blueprint.route('/refresh', methods=['POST'])
def refresh():
    try:
        data = request.get_json()
        refresh_token = data.get('refresh_token')

        if not refresh_token:
            return jsonify({'message': 'Missing refresh token'}), 400

        user_id = verify_token(refresh_token)
        if not user_id:
            return jsonify({'message': 'Invalid or expired refresh token'}), 401

        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404

        new_access_token = generate_access_token(user)

        return jsonify({'access_token': new_access_token}), 200

    except Exception as e:
        return jsonify({'message': str(e)}), 500    

@user_blueprint.route('/protected', methods=['GET'])
@token_required
def protected_route(current_user):
    return jsonify({'message': f'Hello, {current_user.username}. This is a protected route.'})    
