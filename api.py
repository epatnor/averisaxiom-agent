# === File: api.py ===

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

app = FastAPI()

# Logga allt
print("==> Starting AverisAxiom CLEAN Backend...")

# Tillåt CORS för frontend att anropa API:et (ifall JS kör från fil:// etc)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dynamisk sökväg till basen
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
print(f"Base directory: {BASE_DIR}")

# ROOT: servera index.html direkt
@app.get("/")
async def serve_index():
    index_path = os.path.join(BASE_DIR, "index.html")
    print(f"Serving index.html from {index_path}")
    if not os.path.exists(index_path):
        print("index.html not found!")
        return JSONResponse(content={"error": "index.html not found"}, status_code=500)
    return FileResponse(index_path, media_type="text/html")

# Enkel test-API för att säkerställa att backend svarar
@app.get("/api/health")
async def health():
    print("Health check OK")
    return {"status": "ok"}
