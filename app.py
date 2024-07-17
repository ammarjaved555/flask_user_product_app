from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
import jwt
from functools import wraps

app = Flask(__name__)

app.config['SECRET_KEY'] = "secret_key"
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:postgres@localhost:5432/flask_database"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(120), nullable=False)
    confirm_password = db.Column(db.String(120), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.username}>'

# Create tables
with app.app_context():
    db.create_all()

# JWT utility functions
def generate_access_token(user):
    payload = {
        'user_id': user.id,
        'exp': datetime.utcnow() + timedelta(minutes=15)  
    }
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    return token

def generate_refresh_token(user):
    payload = {
        'user_id': user.id,
        'exp': datetime.utcnow() + timedelta(hours=1)  
    }
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    return token

def verify_token(token):
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None  

# Decorator for verifying the token
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Check if the token is passed in the headers
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]  # Bearer token
        
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



# Routes
@app.route('/users', methods=['GET'])
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

# -------------Register-------------
@app.route('/register', methods=['POST'])
def register():
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

# -------------login-------------
@app.route('/login', methods=['POST'])
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

# -------------Refresh Token-------------
@app.route('/refresh', methods=['POST'])
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
    

# -------------Protected Route-------------
@app.route('/protected', methods=['GET'])
@token_required
def protected_route(current_user):
    return jsonify({'message': f'Hello, {current_user.username}. This is a protected route.'})    

if __name__ == '__main__':
    app.run(debug=True, port=8000)
