from flask import Blueprint, jsonify, request, send_from_directory
import traceback
import os
from services.downloader_service import download_video

downloader_bp = Blueprint('downloader', __name__)

@downloader_bp.route('/download_file/<path:filename>')
def download_file(filename):
    return send_from_directory(os.path.join(os.getcwd(), 'downloads'), filename, as_attachment=True)

@downloader_bp.route('/downloader', methods=['POST'])
def handle_download():
    data = request.json
    url = data.get('url')
    print(f"Received URL: {url}")
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    try:
        media_type, title, file_path = download_video(url)
        
        # Determine the filename(s) to send back
        if isinstance(file_path, list):
            filenames = [os.path.basename(f) for f in file_path]
        else:
            filenames = [os.path.basename(file_path)]
            
        return jsonify({
            "status": "success", 
            "message": f"ទាញយក {title} បានជោគជ័យ!",
            "files": filenames,
            "media_type": media_type
        })
    except Exception as e:
        print("--- ERROR OCCURRED ---")
        traceback.print_exc()
        error_msg = str(e)
        # ពិនិត្យមើលថាតើវាជាកំហុសទាក់ទងនឹងការ Login ឬទេ
        if "Log in for access" in error_msg:
            return jsonify({"status": "error", "message": "វីដេអូនេះមានការការពារ (Private/Restricted)។ សូមសាកល្បងវីដេអូផ្សេងទៀត!"}), 403
        
        return jsonify({"status": "error", "message": "មានបញ្ហាក្នុងការទាញយក។ សូមព្យាយាមម្តងទៀត។"}), 500