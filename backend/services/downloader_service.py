import yt_dlp
import requests
import os
import re

def download_video(url, state=None, quality='best'):
    download_folder = 'downloads'
    os.makedirs(download_folder, exist_ok=True)
    
    # ប្រើ tikwm API ជាជម្រើសទី ១ សម្រាប់ TikTok (ដើម្បីចាប់យក Photo Slide)
    if "tiktok.com" in url or "vt.tiktok.com" in url:
        try:
            response = requests.post('https://www.tikwm.com/api/', data={'url': url})
            data = response.json()
            if data.get('code') == 0:
                video_info = data['data']
                title = video_info.get('title', 'TikTok_Media')
                safe_title = re.sub(r'[\\/*?:"<>|]', "", title).strip()[:60].strip()
                if not safe_title:
                    safe_title = "TikTok_Media"
                
                # ពិនិត្យមើលថាវាជាវីដេអូ ឬរូបភាព (Photo Slide)
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
                # If API returned an error for a photo, we should know
                if "/photo/" in url:
                    raise Exception(f"TikWM API Error: {data.get('msg', 'Unknown error')}")
        except Exception as e:
            if "/photo/" in url:
                # yt-dlp doesn't support photo slides, so we might as well show the real error
                raise Exception(f"មិនអាចទាញយករូបភាពពី TikTok បានទេ៖ {str(e)}")
            pass # បើ tikwm បរាជ័យ ហើយមិនមែន photo ទេ បន្តទៅ yt-dlp
    os.makedirs(download_folder, exist_ok=True)
    
    def my_hook(d):
        if state is not None:
            if d['status'] == 'downloading':
                downloaded = d.get('downloaded_bytes', 0)
                total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                if total > 0:
                    state['percent'] = (downloaded / total) * 100
                
                # Clean ANSI escape sequences from speed string
                speed_str = d.get('_speed_str', '')
                if speed_str:
                    speed_str = re.sub(r'\x1b\[[0-9;]*[mG]', '', speed_str)
                    state['speed'] = speed_str.strip()
            elif d['status'] == 'finished':
                state['percent'] = 100
                state['status'] = 'finished'

    # បង្ខំឱ្យវាទាញយកជា mp4 ព្រោះ Telegram មិនគាំទ្រ webm ឱ្យ play ផ្ទាល់ទេ
    format_str = 'best[ext=mp4]/best'
    if quality != 'best':
        format_str = f'bestvideo[height<={quality}][ext=mp4]+bestaudio[ext=m4a]/best[height<={quality}][ext=mp4]/best[ext=mp4]/best'

    ydl_opts = {
        'format': format_str,
        # Truncate title to 80 chars to avoid Windows [Errno 22] Invalid argument / max path length errors
        'outtmpl': f'{download_folder}/%(title).80s.%(ext)s',
        'progress_hooks': [my_hook],
        'quiet': True,
        'noprogress': True,
        'windowsfilenames': True # Ensures strict Windows filename compliance
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            # Use requested_downloads to get the actual final filepath after any merging/converting (e.g. to mp4)
            if 'requested_downloads' in info and len(info['requested_downloads']) > 0:
                filename = info['requested_downloads'][0]['filepath']
            else:
                filename = ydl.prepare_filename(info)
                # In case yt-dlp converted it to mp4 but prepare_filename didn't reflect it
                if not os.path.exists(filename) and os.path.exists(filename.rsplit('.', 1)[0] + '.mp4'):
                    filename = filename.rsplit('.', 1)[0] + '.mp4'
                    
            return ('video', info.get('title', 'Unknown Title'), filename)
    except Exception as e:
        error_msg = str(e)
        
        # បើវីដេអូទាមទារការ Login ឬជា Story/Reel ឬមកពី Facebook ទើបយើងសាកប្រើ Chrome Cookies ជាជម្រើសទី២
        if "login" in error_msg.lower() or "private" in error_msg.lower() or "sign in" in error_msg.lower() or any(x in url.lower() for x in ["story", "stories", "reel", "facebook.com", "fb.watch"]):
            browsers_to_try = ['chrome', 'edge', 'firefox', 'brave', 'opera']
            last_error = error_msg
            
            for browser in browsers_to_try:
                ydl_opts_cookies = ydl_opts.copy()
                ydl_opts_cookies['cookiesfrombrowser'] = (browser, )
                try:
                    with yt_dlp.YoutubeDL(ydl_opts_cookies) as ydl_cookies:
                        info = ydl_cookies.extract_info(url, download=True)
                        if 'requested_downloads' in info and len(info['requested_downloads']) > 0:
                            filename = info['requested_downloads'][0]['filepath']
                        else:
                            filename = ydl_cookies.prepare_filename(info)
                            if not os.path.exists(filename) and os.path.exists(filename.rsplit('.', 1)[0] + '.mp4'):
                                filename = filename.rsplit('.', 1)[0] + '.mp4'
                        return ('video', info.get('title', 'Unknown Title'), filename)
                except Exception as e_cookies:
                    last_error = str(e_cookies)
                    # ប្រសិនបើមានបញ្ហា (ឧទាហរណ៍ មិនមាន Browser នេះ ឬ DPAPI lock) យើងនឹងសាកល្បង Browser បន្ទាប់ទៀត
                    continue
            
            # បើសាកអស់ Browser ហើយនៅតែមិនបាន
            error_msg = re.sub(r'\x1b\[[0-9;]*[mGK]', '', last_error)
        else:
            # សម្អាត ANSI Color codes (ឧទាហរណ៍ [0;31m) ចេញពី Error របស់ yt-dlp សម្រាប់ Error ធម្មតា
            error_msg = re.sub(r'\x1b\[[0-9;]*[mGK]', '', error_msg)
        
        # ប្តូររចនាបថ Error ឱ្យងាយយល់
        if "login.php" in error_msg or "Private video" in error_msg:
            error_msg = "វីដេអូនេះត្រូវបានដាក់ជាឯកជន (Private) ឬទាមទារការចូលគណនី (Login)។ Bot មិនអាចទាញយកបានទេ។"
        elif "Could not copy Chrome cookie database" in error_msg or "database is locked" in error_msg:
            error_msg = "សូមបិទកម្មវិធី Web Browser (Chrome, Edge...) ទាំងស្រុងសិន! ព្រោះ Browser កំពុងចាក់សោរឯកសារទិន្នន័យ (Cookies)។"
        elif "Failed to decrypt with DPAPI" in error_msg:
            error_msg = "Google Chrome/Edge ជំនាន់ថ្មីបានដាក់ប្រព័ន្ធសុវត្ថិភាពខ្ពស់ មិនឱ្យ Bot អាន Cookies ដោយស្វ័យប្រវត្តិបានទេ។ ដំណោះស្រាយ៖ សូមប្រើកម្មវិធី Firefox ឬដំឡើង Extension 'Get cookies.txt' ដើម្បីយកឯកសារ cookies មកប្រើ!"
            
        # បោះកំហុសចេញដើម្បីឱ្យ route អាចចាប់បាន
        raise Exception(f"ការទាញយកមានបញ្ហា: {error_msg}")