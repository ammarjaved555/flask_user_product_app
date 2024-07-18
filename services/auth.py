from datetime import datetime, timedelta
import jwt
from flask import current_app, jsonify, request
from models.user import User
from functools import wraps

def generate_access_token(user):
    payload = {
        'user_id': user.id,
        'exp': datetime.utcnow() + timedelta(minutes=15)  
    }
    token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
    return token

def generate_refresh_token(user):
    payload = {
        'user_id': user.id,
        'exp': datetime.utcnow() + timedelta(hours=1)  
    }
    token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
    return token

def verify_token(token):
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None  

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
