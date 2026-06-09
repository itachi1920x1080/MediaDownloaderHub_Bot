import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from routes.downloader import downloader_bp

# ផ្ទុកទិន្នន័យពីឯកសារ .env
load_dotenv()

app = Flask(__name__)
CORS(app)
app.json.ensure_ascii = False
@app.route('/')
def home():
    return "<h1>Media Downloader Hub API is Running!</h1>"
app.register_blueprint(downloader_bp, url_prefix='/api')

if __name__ == '__main__':
    app.run(debug=True)