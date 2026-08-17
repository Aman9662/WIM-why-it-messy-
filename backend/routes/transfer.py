import os
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from backend.database.db import create_transfer, get_transfer

router = APIRouter(prefix="/api/transfer", tags=["Transfer Service"])

# Store files in a temporary uploads directory
if os.environ.get("VERCEL") or os.environ.get("AWS_EXECUTION_ENV"):
    UPLOAD_DIR = "/tmp/uploads"
else:
    UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

from typing import List
import zipfile

@router.post("/upload")
async def upload_file(files: List[UploadFile] = File(...)):
    if len(files) == 1:
        file = files[0]
        unique_filename = f"{os.urandom(8).hex()}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        with open(file_path, "wb") as f:
            f.write(await file.read())
            
        code = create_transfer(file.filename, file_path, minutes=10)
        return {"code": code, "expires_in": "10 minutes", "file_name": file.filename}
    else:
        zip_filename = f"{os.urandom(8).hex()}_archive.zip"
        zip_path = os.path.join(UPLOAD_DIR, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in files:
                zipf.writestr(file.filename, await file.read())
                
        display_name = f"{len(files)} files (Archive)"
        code = create_transfer(display_name, zip_path, minutes=10)
        return {"code": code, "expires_in": "10 minutes", "file_name": display_name}

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
