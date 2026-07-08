from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=True) # Nullable for OAuth users
    auth_provider = db.Column(db.String(20), default="local") # "local" or "google"
    oauth_id = db.Column(db.String(255), nullable=True, unique=True)
    avatar = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    downloads = db.relationship('DownloadHistory', backref='user', lazy=True)

class DownloadHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    url = db.Column(db.Text, nullable=False)
    format = db.Column(db.String(20), nullable=True) # mp4, mp3
    quality = db.Column(db.String(50), nullable=True) # 1080p, 720p, etc
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
