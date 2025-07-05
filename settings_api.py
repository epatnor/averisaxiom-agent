# settings_api.py

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import settings_db

router = APIRouter()

# Ensure DB exists on import
settings_db.init_settings_db()

@router.get("/settings")
def get_settings():
    # Fetch settings and metadata
    settings, metadata = settings_db.get_all_settings(include_metadata=True)
    print("==> [API] Fetched settings with metadata:")
    for key in sorted(settings):
        masked = metadata[key]["masked"]
        dummy = metadata[key]["is_dummy"]
        print(f"    {key} = {masked}" + (" (DUMMY)" if dummy else ""))
    return settings

@router.post("/settings")
async def save_settings(request: Request):
    # Receive and store updated settings
    data = await request.json()
    print("==> [API] Saving incoming settings:")
    for k, v in data.items():
        print(f"    {k} = {settings_db.redact_sensitive(k, v)}")
        settings_db.set_setting(k, v)
    return {"status": "saved"}
