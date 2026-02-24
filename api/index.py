import os
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp

app = FastAPI()

# Izinkan Frontend di GitHub Pages mengakses ini
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Ganti 'SECRET_TOKEN_123' dengan kode rahasia pilihan Anda di Env Variable Vercel
API_KEY = os.environ.get("API_KEY", "SECRET_TOKEN_123")

@app.get("/api/extract")
async def extract_video(url: str, x_api_key: str = Header(None)):
    # Validasi API Key dari Header (disembunyikan di JS)
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized")

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'format': 'best',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            formats_list = []
            for f in info.get('formats', []):
                if not f.get('url'): continue
                
                # Metadata Resolusi
                height = f.get('height')
                ext = f.get('ext')
                vcodec = f.get('vcodec')
                acodec = f.get('acodec')
                
                # Tentukan Tipe
                if vcodec != 'none' and acodec != 'none':
                    ftype = "Video + Audio"
                elif vcodec != 'none':
                    ftype = "Video (No Sound)"
                else:
                    ftype = "Audio Only"

                # Filter hanya resolusi yang berguna (sampai 1080p)
                label = f"{height}p" if height else "Audio"
                
                formats_list.append({
                    "id": f.get('format_id'),
                    "url": f.get('url'),
                    "ext": ext,
                    "resolution": label,
                    "type": ftype,
                    "size": f.get('filesize')
                })

            return {
                "title": info.get('title'),
                "thumbnail": info.get('thumbnail'),
                "duration": info.get('duration'),
                "formats": formats_list
            }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
