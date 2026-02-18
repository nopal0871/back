from flask import Flask, request, jsonify, send_file
from yt_dlp import YoutubeDL
import os, tempfile, uuid

app = Flask(__name__)
os.makedirs("downloads", exist_ok=True)

@app.route("/download", methods=["POST"])
def download():
    data = request.json
    url = data.get("url")
    fmt = data.get("format", "video")
    
    if not url:
        return jsonify({"error": "URL ora ono, cuk 🗿"}), 400
    
    ydl_opts = {
        "outtmpl": f"downloads/%(id)s.%(ext)s",
        "quiet": True,
        "no_warnings": True,
    }
    
    if fmt == "audio":
        ydl_opts.update({
            "format": "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
        })
    else:
        ydl_opts["format"] = "bestvideo+bestaudio/best"
    
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if fmt == "audio":
                filename = filename.rsplit(".", 1)[0] + ".mp3"
            
            # Kirim file (di production, pake cloud storage!)
            return send_file(filename, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
