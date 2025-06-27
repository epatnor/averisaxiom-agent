from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import settings_db

# Init the router for settings endpoints
router = APIRouter()

# Ensure settings DB is initialized at import
settings_db.init_settings_db()

@router.get("/settings")
def get_settings():
    """
    Load all settings from the settings database.
    """
    settings = settings_db.get_all_settings()
    print("==> [API] Fetched settings:")
    for k, v in settings.items():
        print(f"    {k} = {v}")
    return settings

@router.post("/settings")
async def save_settings(request: Request):
    """
    Save incoming settings (as key-value pairs) to the settings database.
    """
    data = await request.json()
    print("==> [API] Saving incoming settings:")
    for k, v in data.items():
        print(f"    {k} = {v}")
        settings_db.set_setting(k, v)
    return {"status": "saved"}
