import os
from flask import Blueprint, request, jsonify, redirect, current_app, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import db, User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400
        
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 400

    hashed_password = generate_password_hash(password)
    new_user = User(username=username, password_hash=hashed_password, auth_provider='local')
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User created successfully'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if not user or not user.password_hash or not check_password_hash(user.password_hash, password):
        return jsonify({'error': 'Invalid username or password'}), 401

    access_token = create_access_token(identity=str(user.id))
    return jsonify({'token': access_token, 'username': user.username}), 200

@auth_bp.route('/google/login')
def google_login():
    oauth = current_app.extensions['oauth']
    redirect_uri = url_for('auth.google_callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@auth_bp.route('/google/callback')
def google_callback():
    try:
        oauth = current_app.extensions['oauth']
        token = oauth.google.authorize_access_token()
        user_info = token.get('userinfo')
        
        oauth_id = user_info.get('sub')
        email = user_info.get('email')
        name = user_info.get('name')
        avatar = user_info.get('picture')
        
        user = User.query.filter_by(oauth_id=oauth_id).first()
        if not user:
            # Maybe they registered locally but now used Google? We could link by email, but keeping it simple:
            user = User(
                username=email.split('@')[0],
                email=email,
                auth_provider='google',
                oauth_id=oauth_id,
                avatar=avatar
            )
            db.session.add(user)
            db.session.commit()
        else:
            user.avatar = avatar
            db.session.commit()
            
        access_token = create_access_token(identity=str(user.id))
        
        # Redirect to frontend with token
        frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:5173")
        return redirect(f"{frontend_url}/?token={access_token}&username={user.username}")
        
    except Exception as e:
        print(f"OAuth Error: {e}")
        frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:5173")
        return redirect(f"{frontend_url}/login?error=oauth_failed")


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_me():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({'username': user.username, 'avatar': user.avatar}), 200
