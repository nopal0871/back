from flask import Flask, request, jsonify, send_file, make_response
from yt_dlp import YoutubeDL
import os
import tempfile
import uuid
import shutil
from flask_cors import CORS  # ← TAMBAHNO KIYE!

# Init Flask app
app = Flask(__name__)

# CORS Headers - WAJIB kanggo Vercel!
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Max-Age', '86400')
    return response

# Handle preflight OPTIONS request
@app.route('/', methods=['OPTIONS'])
@app.route('/download', methods=['OPTIONS'])
def options_handler():
    response = make_response('', 200)
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Root endpoint - kanggo test
@app.route('/', methods=['GET'])
def index():
    return jsonify({
        'status': 'ok',
        'message': 'Backend is running! 🗿',
        'endpoints': {
            'download': 'POST /download',
            'body': {'url': 'video_url', 'format': 'video|audio'}
        }
    })

# Download endpoint
@app.route('/download', methods=['POST'])
def download():
    download_dir = None
    
    try:
        # Get JSON data
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided', 'message': 'Kirim JSON bangsat! 🗿'}), 400
        
        # Get parameters
        url = data.get('url')
        format_type = data.get('format', 'video')
        
        # Validate URL
        if not url:
            return jsonify({'error': 'URL is required', 'message': 'URL-e endi, Cuk? 🤣'}), 400
        
        # Create temporary directory
        download_dir = f"/tmp/downloads_{uuid.uuid4().hex}"
        os.makedirs(download_dir, exist_ok=True)
        
        # Configure yt-dlp options
        ydl_opts = {
            'outtmpl': f'{download_dir}/%(id)s.%(ext)s',
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'ignoreerrors': False,
        }
        
        # Set format based on type
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
            # Video - download best quality
            ydl_opts.update({
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'merge_output_format': 'mp4',
            })
        
        # Download video/audio
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
            if not info:
                return jsonify({'error': 'Failed to extract info', 'message': 'URL ora valid, Cuk! 🗿'}), 400
            
            # Determine filename
            filename = ydl.prepare_filename(info)
            
            # For audio, change extension to mp3
            if format_type == 'audio':
                filename = filename.rsplit('.', 1)[0] + '.mp3'
            
            # Check if file exists
            if not os.path.exists(filename):
                # Try to find file with different extension
                base_name = filename.rsplit('.', 1)[0]
                for ext in ['mp4', 'mkv', 'webm', 'mp3', 'm4a']:
                    test_file = f'{base_name}.{ext}'
                    if os.path.exists(test_file):
                        filename = test_file
                        break
            
            # Get file size
            file_size = os.path.getsize(filename) if os.path.exists(filename) else 0
            
            if file_size == 0:
                return jsonify({'error': 'File empty or not found', 'message': 'File kosong, Cuk! 💔'}), 500
            
            # Send file
            return send_file(
                filename,
                as_attachment=True,
                download_name=os.path.basename(filename),
                mimetype='video/mp4' if format_type == 'video' else 'audio/mpeg'
            )
            
    except Exception as e:
        error_msg = str(e)
        print(f"ERROR: {error_msg}")  # Log error
        return jsonify({
            'error': 'Download failed',
            'message': f'Error: {error_msg}',
            'tip': 'Cek URL-e bener apa ora, Cuk! 🤣'
        }), 500
    
    finally:
        # Cleanup - hapus temporary files
        if download_dir and os.path.exists(download_dir):
            try:
                shutil.rmtree(download_dir, ignore_errors=True)
            except:
                pass

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found', 'message': '404 - Ora ono, Cuk! 🗿'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error', 'message': '500 - Server error, Cuk! 💔'}), 500

# JANGAN ADA handler() FUNCTION!
# Flask app otomatis di-export kanggo Vercel
