import yt_dlp
import requests
import os
import re

def download_video(url, state=None, quality='best', format_choice='mp4', is_playlist=False):
    download_folder = 'downloads'
    os.makedirs(download_folder, exist_ok=True)
    
    # Use tikwm API for TikTok (to catch Photo Slides), but only for single videos and mp4 format
    if ("tiktok.com" in url or "vt.tiktok.com" in url) and not is_playlist and format_choice == 'mp4':
        try:
            response = requests.post('https://www.tikwm.com/api/', data={'url': url})
            data = response.json()
            if data.get('code') == 0:
                video_info = data['data']
                title = video_info.get('title', 'TikTok_Media')
                safe_title = re.sub(r'[\\/*?:"<>|]', "", title).strip()[:60].strip()
                if not safe_title:
                    safe_title = "TikTok_Media"
                
                # Check for images (Photo Slide)
                if 'images' in video_info and isinstance(video_info['images'], list):
                    image_paths = []
                    for idx, img_url in enumerate(video_info['images']):
                        img_path = f"{download_folder}/{safe_title}_{idx}.jpeg"
                        img_resp = requests.get(img_url)
                        if img_resp.status_code == 200:
                            with open(img_path, 'wb') as f:
                                f.write(img_resp.content)
                            image_paths.append(img_path)
                    
                    if state is not None:
                        state['percent'] = 100
                        state['status'] = 'finished'
                    return ('images', title, image_paths)
                
                play_url = video_info.get('play')
                if play_url:
                    filepath = f"{download_folder}/{safe_title}.mp4"
                    video_resp = requests.get(play_url, stream=True)
                    if video_resp.status_code == 200:
                        total_size = int(video_resp.headers.get('content-length', 0))
                        downloaded_size = 0
                        with open(filepath, 'wb') as f:
                            for chunk in video_resp.iter_content(chunk_size=1024*1024):
                                if chunk:
                                    f.write(chunk)
                                    downloaded_size += len(chunk)
                                    if state is not None and total_size > 0:
                                        state['percent'] = (downloaded_size / total_size) * 100
                        if state is not None:
                            state['percent'] = 100
                            state['status'] = 'finished'
                        return ('video', title, filepath)
            else:
                if "/photo/" in url:
                    raise Exception(f"TikWM API Error: {data.get('msg', 'Unknown error')}")
        except Exception as e:
            if "/photo/" in url:
                raise Exception(f"Cannot download TikTok photos: {str(e)}")
            pass # Fallback to yt-dlp if tikwm fails
            
    os.makedirs(download_folder, exist_ok=True)
    
    def my_hook(d):
        if state is not None:
            if d['status'] == 'downloading':
                downloaded = d.get('downloaded_bytes', 0)
                total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                if total > 0:
                    state['percent'] = (downloaded / total) * 100
                
                speed_str = d.get('_speed_str', '')
                if speed_str:
                    speed_str = re.sub(r'\x1b\[[0-9;]*[mG]', '', speed_str)
                    state['speed'] = speed_str.strip()
            elif d['status'] == 'finished':
                if state.get('percent', 0) < 100:
                     # It might be downloading the next item in a playlist or postprocessing
                     state['speed'] = 'Processing...'

    ydl_opts = {
        'outtmpl': f'{download_folder}/%(title).80s.%(ext)s',
        'progress_hooks': [my_hook],
        'quiet': True,
        'noprogress': True,
        'windowsfilenames': True,
        'noplaylist': not is_playlist
    }

    if format_choice == 'mp3':
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    else:
        format_str = 'best[ext=mp4]/best'
        if quality != 'best':
            format_str = f'bestvideo[height<={quality}][ext=mp4]+bestaudio[ext=m4a]/best[height<={quality}][ext=mp4]/best[ext=mp4]/best'
        ydl_opts['format'] = format_str

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
            if 'entries' in info:
                # It's a playlist
                title = info.get('title', 'Playlist')
                downloaded_files = []
                for entry in info['entries']:
                    if entry:
                        expected_ext = 'mp3' if format_choice == 'mp3' else 'mp4'
                        base_filename = ydl.prepare_filename(entry).rsplit('.', 1)[0]
                        final_filename = f"{base_filename}.{expected_ext}"
                        if os.path.exists(final_filename):
                            downloaded_files.append(final_filename)
                        else:
                            # In case it didn't convert
                            downloaded_files.append(ydl.prepare_filename(entry))
                            
                return ('playlist', title, downloaded_files)
            else:
                title = info.get('title', 'Unknown Title')
                if 'requested_downloads' in info and len(info['requested_downloads']) > 0:
                    filename = info['requested_downloads'][0]['filepath']
                else:
                    filename = ydl.prepare_filename(info)
                    
                    expected_ext = 'mp3' if format_choice == 'mp3' else 'mp4'
                    if not filename.endswith(f'.{expected_ext}'):
                        converted = filename.rsplit('.', 1)[0] + f'.{expected_ext}'
                        if os.path.exists(converted):
                            filename = converted
                            
                return ('audio' if format_choice == 'mp3' else 'video', title, filename)
    except Exception as e:
        error_msg = str(e)
        
        # Retry with browser cookies for restricted content
        if "login" in error_msg.lower() or "private" in error_msg.lower() or "sign in" in error_msg.lower() or any(x in url.lower() for x in ["story", "stories", "reel", "facebook.com", "fb.watch"]):
            browsers_to_try = ['chrome', 'edge', 'firefox', 'brave', 'opera']
            last_error = error_msg
            
            for browser in browsers_to_try:
                ydl_opts_cookies = ydl_opts.copy()
                ydl_opts_cookies['cookiesfrombrowser'] = (browser, )
                try:
                    with yt_dlp.YoutubeDL(ydl_opts_cookies) as ydl_cookies:
                        info = ydl_cookies.extract_info(url, download=True)
                        
                        if 'entries' in info:
                            title = info.get('title', 'Playlist')
                            downloaded_files = []
                            for entry in info['entries']:
                                if entry:
                                    expected_ext = 'mp3' if format_choice == 'mp3' else 'mp4'
                                    base_filename = ydl_cookies.prepare_filename(entry).rsplit('.', 1)[0]
                                    final_filename = f"{base_filename}.{expected_ext}"
                                    if os.path.exists(final_filename):
                                        downloaded_files.append(final_filename)
                                    else:
                                        downloaded_files.append(ydl_cookies.prepare_filename(entry))
                            return ('playlist', title, downloaded_files)
                        else:
                            title = info.get('title', 'Unknown Title')
                            if 'requested_downloads' in info and len(info['requested_downloads']) > 0:
                                filename = info['requested_downloads'][0]['filepath']
                            else:
                                filename = ydl_cookies.prepare_filename(info)
                                expected_ext = 'mp3' if format_choice == 'mp3' else 'mp4'
                                if not filename.endswith(f'.{expected_ext}'):
                                    converted = filename.rsplit('.', 1)[0] + f'.{expected_ext}'
                                    if os.path.exists(converted):
                                        filename = converted
                            return ('audio' if format_choice == 'mp3' else 'video', title, filename)
                except Exception as e_cookies:
                    e_str = str(e_cookies)
                    if "could not find" not in e_str.lower() and "no such file" not in e_str.lower():
                        last_error = e_str
                    continue
            
            error_msg = re.sub(r'\x1b\[[0-9;]*[mGK]', '', last_error)
        else:
            error_msg = re.sub(r'\x1b\[[0-9;]*[mGK]', '', error_msg)
        
        if "login.php" in error_msg or "Private video" in error_msg:
            error_msg = "Video is private or requires login."
        elif "Could not copy Chrome cookie database" in error_msg or "database is locked" in error_msg:
            error_msg = "Please close your browser first! Browser is locking the cookies."
        elif "Failed to decrypt with DPAPI" in error_msg:
            error_msg = "Browser blocked cookie access. Please use Firefox or a cookies.txt extension."
        elif "sign in to confirm" in error_msg.lower():
            error_msg = "YouTube requires login to verify you are not a bot. Cookies are needed."
            
        raise Exception(f"Download failed: {error_msg}")