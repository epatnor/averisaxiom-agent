from fastapi import APIRouter, HTTPException, Request
from settings_db import get_all_settings, get_setting, set_setting

router = APIRouter()

@router.get("/api/settings")
def read_settings():
    """Return all settings as a dictionary."""
    return get_all_settings()

@router.post("/api/settings")
async def save_settings(request: Request):
    """Update multiple settings based on posted JSON."""
    data = await request.json()
    if not isinstance(data, dict):
        raise HTTPException(status_code=400, detail="Invalid JSON")

    for key, value in data.items():
        set_setting(key, value)
    return {"status": "success", "updated": list(data.keys())}
