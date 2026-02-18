from flask import Flask, request, jsonify, send_file
from yt_dlp import YoutubeDL
import os
import tempfile
import uuid

# Gawe Flask app
app = Flask(__name__)

@app.route('/download', methods=['POST'])
def download():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data'}), 400
        
        url = data.get('url')
        format_type = data.get('format', 'video')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Gawe temporary directory
        download_dir = f"/tmp/downloads_{uuid.uuid4().hex}"
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
        
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            if format_type == 'audio':
                filename = filename.rsplit('.', 1)[0] + '.mp3'
            
            # Send file
            return send_file(
                filename,
                as_attachment=True,
                download_name=os.path.basename(filename)
            )
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    finally:
        # Cleanup
        import shutil
        if os.path.exists(download_dir):
            shutil.rmtree(download_dir, ignore_errors=True)

# Route test
@app.route('/', methods=['GET'])
def index():
    return jsonify({'status': 'ok', 'message': 'Backend is running! 🗿'})

# Export app kanggo Vercel
# JANGAN ADA handler() FUNCTION!
