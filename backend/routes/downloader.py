from flask import Blueprint, jsonify, request, send_from_directory, Response
import traceback
import os
import uuid
import threading
import json
import time
from services.downloader_service import download_video
from models import db, DownloadHistory
from flask_jwt_extended import jwt_required, get_jwt_identity

downloader_bp = Blueprint('downloader', __name__)

# In-memory dictionary to store download progress for SSE
progress_states = {}

@downloader_bp.route('/download_file/<path:filename>')
def download_file(filename):
    return send_from_directory(os.path.join(os.getcwd(), 'downloads'), filename, as_attachment=True)

def download_task(task_id, url, user_id, format_choice, quality, is_playlist, app_context):
    with app_context:
        try:
            progress_states[task_id]['status'] = 'downloading'
            media_type, title, file_path = download_video(
                url, 
                state=progress_states[task_id], 
                quality=quality, 
                format_choice=format_choice, 
                is_playlist=is_playlist
            )
            
            # Save to history if logged in
            if user_id:
                history_entry = DownloadHistory(
                    user_id=user_id,
                    title=title,
                    url=url,
                    format=format_choice,
                    quality=quality
                )
                db.session.add(history_entry)
                db.session.commit()

            if isinstance(file_path, list):
                filenames = [os.path.basename(f) for f in file_path]
            else:
                filenames = [os.path.basename(file_path)]
                
            progress_states[task_id]['status'] = 'success'
            progress_states[task_id]['files'] = filenames
            progress_states[task_id]['media_type'] = media_type
            progress_states[task_id]['title'] = title
            
        except Exception as e:
            traceback.print_exc()
            progress_states[task_id]['status'] = 'error'
            error_msg = str(e)
            if "Log in for access" in error_msg:
                progress_states[task_id]['message'] = "វីដេអូនេះមានការការពារ (Private/Restricted)។ សូមសាកល្បងវីដេអូផ្សេងទៀត!"
            else:
                progress_states[task_id]['message'] = error_msg

@downloader_bp.route('/downloader', methods=['POST'])
@jwt_required(optional=True)
def handle_download():
    data = request.json
    url = data.get('url')
    format_choice = data.get('format', 'mp4') # mp4 or mp3
    quality = data.get('quality', 'best')
    is_playlist = data.get('is_playlist', False)
    
    current_user_id = get_jwt_identity()
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
        
    task_id = str(uuid.uuid4())
    progress_states[task_id] = {'percent': 0, 'speed': '', 'status': 'queued'}
    
    from flask import current_app
    app_context = current_app.app_context()
    
    thread = threading.Thread(
        target=download_task, 
        args=(task_id, url, current_user_id, format_choice, quality, is_playlist, app_context)
    )
    thread.start()
    
    return jsonify({
        "status": "started",
        "task_id": task_id,
        "message": "Download task started"
    })

@downloader_bp.route('/progress/<task_id>')
def get_progress(task_id):
    def generate():
        while True:
            if task_id not in progress_states:
                yield f"data: {json.dumps({'status': 'error', 'message': 'Task not found'})}\n\n"
                break
                
            state = progress_states[task_id]
            yield f"data: {json.dumps(state)}\n\n"
            
            if state['status'] in ['success', 'error']:
                # Clean up after sending final state
                time.sleep(1) # Give client time to receive
                del progress_states[task_id]
                break
                
            time.sleep(0.5)
            
    return Response(generate(), mimetype='text/event-stream')