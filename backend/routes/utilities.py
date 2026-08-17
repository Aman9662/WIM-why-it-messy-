from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import Response
from io import BytesIO
import time
from PIL import Image
from pypdf import PdfReader, PdfWriter
import os

router = APIRouter(prefix="/api/utils", tags=["Utilities"])

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

@router.post("/compress-image")
async def compress_image(file: UploadFile = File(...), quality: int = Form(60)):
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(400, "File too large (max 50MB).")
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "File must be an image.")
    try:
        img = Image.open(BytesIO(content))
        out_io = BytesIO()
        
        # Convert to RGB if needed to save as JPEG
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
            
        img.save(out_io, format="JPEG", optimize=True, quality=quality)
        
        filename = f"compressed_{file.filename.rsplit('.', 1)[0]}.jpg"
        return Response(
            content=out_io.getvalue(), 
            media_type="image/jpeg", 
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        from PIL import UnidentifiedImageError
        if isinstance(e, (UnidentifiedImageError, OSError)):
            raise HTTPException(400, f"Invalid or corrupted image: {str(e)}")
        raise HTTPException(500, f"Error processing image: {str(e)}")

@router.post("/resize-image")
async def resize_image(file: UploadFile = File(...), width: int = Form(...), height: int = Form(...)):
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(400, "File too large (max 50MB).")
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "File must be an image.")
    
    try:
        img = Image.open(BytesIO(content))
        # Use Lanczos for high-quality downsampling
        img = img.resize((width, height), Image.Resampling.LANCZOS)
        
        out_io = BytesIO()
        
        # Save in the original format based on filename if possible, otherwise PNG
        filename, ext = os.path.splitext(file.filename)
        ext = ext.lower().replace('.', '')
        format_map = {'jpg': 'JPEG', 'jpeg': 'JPEG', 'png': 'PNG', 'webp': 'WEBP', 'gif': 'GIF'}
        format = format_map.get(ext, "PNG")

        if format == "JPEG" and img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
            
        img.save(out_io, format=format)
        
        return Response(
            content=out_io.getvalue(), 
            media_type=file.content_type, 
            headers={"Content-Disposition": f"attachment; filename=resized_{file.filename}"}
        )
    except Exception as e:
        from PIL import UnidentifiedImageError
        if isinstance(e, (UnidentifiedImageError, OSError)):
            raise HTTPException(400, f"Invalid or corrupted image: {str(e)}")
        raise HTTPException(500, f"Error resizing image: {str(e)}")

@router.post("/compress-pdf")
async def compress_pdf(file: UploadFile = File(...)):
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(400, "File too large (max 50MB).")
    if file.content_type != "application/pdf" and not file.filename.endswith(".pdf"):
        raise HTTPException(400, "File must be a PDF.")
    
    try:
        reader = PdfReader(BytesIO(content))
        writer = PdfWriter()

        # Add all pages to the writer first
        for page in reader.pages:
            writer.add_page(page)
            
        # Now compress content streams on the writer's pages
        for page in writer.pages:
            page.compress_content_streams()

        # Write to memory
        out_io = BytesIO()
        
        # Remove images to drastically reduce size for text docs
        writer.remove_images()
        writer.write(out_io)
        
        return Response(
            content=out_io.getvalue(), 
            media_type="application/pdf", 
            headers={"Content-Disposition": f"attachment; filename=compressed_{file.filename}"}
        )
    except Exception as e:
        raise HTTPException(500, f"Error processing PDF: {str(e)}")

@router.post("/target-size-image")
async def target_size_image(file: UploadFile = File(...), target_kb: int = Form(...)):
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(400, "File too large (max 50MB).")
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "File must be an image.")
    
    target_bytes = target_kb * 1024
    if len(content) <= target_bytes:
        return Response(content=content, media_type=file.content_type, headers={"Content-Disposition": f"attachment; filename={file.filename}"})
    
    try:
        img = Image.open(BytesIO(content))
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        
        low, high = 10, 95
        best_data = None
        
        # Binary search for optimal quality
        for _ in range(7):
            mid = (low + high) // 2
            out_io = BytesIO()
            img.save(out_io, format="JPEG", optimize=True, quality=mid)
            size = len(out_io.getvalue())
            
            if size <= target_bytes:
                best_data = out_io.getvalue()
                low = mid + 1
            else:
                high = mid - 1
                
        if not best_data:
            # Fallback to lowest quality if target is extremely small
            out_io = BytesIO()
            img.save(out_io, format="JPEG", optimize=True, quality=10)
            best_data = out_io.getvalue()
            
        filename = f"target_size_{file.filename.rsplit('.', 1)[0]}.jpg"
        return Response(
            content=best_data, 
            media_type="image/jpeg", 
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        from PIL import UnidentifiedImageError
        if isinstance(e, (UnidentifiedImageError, OSError)):
            raise HTTPException(400, f"Invalid or corrupted image: {str(e)}")
        raise HTTPException(500, f"Error reaching target image size: {str(e)}")

@router.post("/target-size-pdf")
async def target_size_pdf(file: UploadFile = File(...), target_kb: int = Form(...)):
    # Precise PDF target sizing requires Ghostscript/external tools.
    # We will use heavy compression if the file is over target size.
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(400, "File too large (max 50MB).")
    if file.content_type != "application/pdf" and not file.filename.endswith(".pdf"):
        raise HTTPException(400, "File must be a PDF.")
        
    target_bytes = target_kb * 1024
    if len(content) <= target_bytes:
        return Response(content=content, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename={file.filename}"})
        
    try:
        reader = PdfReader(BytesIO(content))
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
            
        for page in writer.pages:
            page.compress_content_streams()
            
        out_io = BytesIO()
        writer.remove_images()
        writer.write(out_io)
        
        return Response(
            content=out_io.getvalue(), 
            media_type="application/pdf", 
            headers={"Content-Disposition": f"attachment; filename=target_size_{file.filename}"}
        )
    except Exception as e:
        raise HTTPException(500, f"Error processing PDF: {str(e)}")
