from flask import Blueprint, jsonify, request
from services.downloader_service import download_video

downloader_bp = Blueprint('downloader', __name__)
@downloader_bp.route('/downloader', methods=['POST'])
def handle_download():
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    try:
        title, file_path = download_video(url)
        return jsonify({"status": "success", "message": f"ទាញយក {title} បានជោគជ័យ!"})
    except Exception as e:
        error_msg = str(e)
        # ពិនិត្យមើលថាតើវាជាកំហុសទាក់ទងនឹងការ Login ឬទេ
        if "Log in for access" in error_msg:
            return jsonify({"status": "error", "message": "វីដេអូនេះមានការការពារ (Private/Restricted)។ សូមសាកល្បងវីដេអូផ្សេងទៀត!"}), 403
        
        return jsonify({"status": "error", "message": "មានបញ្ហាក្នុងការទាញយក។ សូមព្យាយាមម្តងទៀត។"}), 500