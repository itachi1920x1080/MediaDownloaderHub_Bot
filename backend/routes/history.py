from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import DownloadHistory

history_bp = Blueprint('history', __name__)

@history_bp.route('/', methods=['GET'])
@jwt_required()
def get_history():
    current_user_id = get_jwt_identity()
    history = DownloadHistory.query.filter_by(user_id=current_user_id).order_by(DownloadHistory.created_at.desc()).all()
    
    return jsonify([{
        'id': h.id,
        'title': h.title,
        'url': h.url,
        'format': h.format,
        'quality': h.quality,
        'timestamp': h.created_at.isoformat()
    } for h in history]), 200
