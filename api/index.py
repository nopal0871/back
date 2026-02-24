import os
from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp

app = FastAPI()

# PENTING: Izinkan akses dari GitHub Pages Anda
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Anda bisa mengganti "*" dengan URL GitHub Pages Anda nanti
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = os.environ.get("API_KEY", "admin123")
API_KEY_NAME = "X-API-KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def validate_api_key(header_value: str = Security(api_key_header)):
    if header_value == API_KEY:
        return header_value
    raise HTTPException(status_code=403, detail="API Key Salah atau Tidak Ada")

@app.get("/api/info")
async def get_video_info(url: str, api_key: str = Depends(validate_api_key)):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'format': 'best',
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = []
            
            for f in info.get('formats', []):
                if f.get('url'):
                    # Filter resolusi atau keterangan audio
                    res = f.get('resolution') or f.get('format_note') or "Unknown"
                    is_audio = f.get('vcodec') == 'none'
                    
                    formats.append({
                        'format_id': f.get('format_id'),
                        'ext': f.get('ext'),
                        'resolution': res,
                        'url': f.get('url'),
                        'type': 'audio' if is_audio else 'video'
                    })

            return {
                "title": info.get('title'),
                "thumbnail": info.get('thumbnail'),
                "duration": f"{info.get('duration', 0) // 60}:{info.get('duration', 0) % 60:02d}",
                "source": info.get('extractor_key'),
                "formats": formats
            }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
