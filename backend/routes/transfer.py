import os
import shutil
import zipfile
import re
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from backend.database.db import create_transfer, get_transfer
from typing import List

router = APIRouter(prefix="/api/transfer", tags=["Transfer Service"])

# Store files in a temporary uploads directory
if os.environ.get("VERCEL") or os.environ.get("AWS_EXECUTION_ENV"):
    UPLOAD_DIR = "/tmp/uploads"
else:
    UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

MAX_TRANSFER_SIZE = 100 * 1024 * 1024  # 100 MB

def sanitize_filename(filename: str) -> str:
    """Basic sanitization for safe filenames."""
    filename = os.path.basename(filename)
    filename = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', filename)
    return filename or "unnamed_file"

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file.file.seek(0, os.SEEK_END)
    total_size = file.file.tell()
    file.file.seek(0)
        
    if total_size > MAX_TRANSFER_SIZE:
        raise HTTPException(400, "Transfer size exceeds 100MB limit.")

    safe_name = sanitize_filename(file.filename)
    file_path = os.path.join(UPLOAD_DIR, f"{os.urandom(8).hex()}_{safe_name}")
    
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
        
    code = create_transfer(safe_name, file_path, minutes=10)
    return {"code": code, "expires_in": "10 minutes", "file_name": safe_name}

@router.get("/download/{code}")
async def download_file(code: str):
    data = get_transfer(code)
    if not data:
        raise HTTPException(404, "Invalid or expired code")
        
    if not os.path.exists(data["file_path"]):
        raise HTTPException(404, "File not found on server")
        
    return FileResponse(
        data["file_path"], 
        media_type="application/octet-stream", 
        headers={"Content-Disposition": f"attachment; filename={data['file_name']}"}
    )

@router.delete("/delete/{code}")
async def delete_file(code: str):
    from backend.database.db import delete_transfer, get_transfer
    data = get_transfer(code)
    if data:
        if os.path.exists(data["file_path"]):
            os.remove(data["file_path"])
        delete_transfer(code)
    return {"status": "deleted"}
