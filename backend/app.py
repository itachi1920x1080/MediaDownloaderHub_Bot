import os
from flask import Flask, session
from flask_cors import CORS
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager
from authlib.integrations.flask_client import OAuth
from models import db
from routes.downloader import downloader_bp
from routes.auth import auth_bp
from routes.history import history_bp

load_dotenv()

app = Flask(__name__)
# Add session cookie setup
app.secret_key = os.environ.get("SECRET_KEY", "super-secret-key")
# Make sure frontend can accept cookies for sessions if needed, though JWT is mostly used
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)
app.json.ensure_ascii = False

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///webapp.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# JWT configuration
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'super-secret-default-key-please-change-in-prod')

# Initialize extensions
db.init_app(app)
jwt = JWTManager(app)

# Initialize OAuth
oauth = OAuth(app)
oauth.register(
    name='google',
    client_id=os.environ.get("GOOGLE_CLIENT_ID"),
    client_secret=os.environ.get("GOOGLE_CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)
app.extensions['oauth'] = oauth # Make oauth accessible in blueprints

# Create tables if they don't exist
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return "<h1>Media Downloader Hub API is Running!</h1>"

app.register_blueprint(downloader_bp, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(history_bp, url_prefix='/api/history')

if __name__ == '__main__':
    app.run(debug=True, port=5000)