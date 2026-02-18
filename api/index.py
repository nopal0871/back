# backend/api/index.py
from flask import Flask, request, jsonify, send_file
from yt_dlp import YoutubeDL
import os
import tempfile
import uuid

app = Flask(__name__)

# Import logic saka main.py (opsional)
# Utawa tulis langsung kene

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    url = data.get('url')
    format_type = data.get('format', 'video')
    
    if not url:
        return jsonify({'error': 'URL ora ono, Cuk! 🗿'}), 400
    
    # Gawe folder临时
    download_dir = f"/tmp/downloads_{uuid.uuid4()}"
    os.makedirs(download_dir, exist_ok=True)
    
    ydl_opts = {
        'outtmpl': f'{download_dir}/%(id)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
    }
    
    if format_type == 'audio':
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        })
    else:
        ydl_opts['format'] = 'bestvideo+bestaudio/best'
    
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            if format_type == 'audio':
                filename = filename.rsplit('.', 1)[0] + '.mp3'
            
            # Kirim file
            return send_file(
                filename,
                as_attachment=True,
                download_name=os.path.basename(filename)
            )
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        # Cleanup (opsional)
        import shutil
        if os.path.exists(download_dir):
            shutil.rmtree(download_dir)

# Export handler kanggo Vercel
def handler(request):
    return app(request.environ, lambda *args: None)
