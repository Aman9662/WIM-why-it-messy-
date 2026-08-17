from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import Response
from io import BytesIO
import time
from PIL import Image
from pypdf import PdfReader, PdfWriter
import os

router = APIRouter(prefix="/api/utils", tags=["Utilities"])

@router.post("/compress-image")
async def compress_image(file: UploadFile = File(...), quality: int = Form(60)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "File must be an image.")
    
    content = await file.read()
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
        raise HTTPException(500, f"Error processing image: {str(e)}")

@router.post("/resize-image")
async def resize_image(file: UploadFile = File(...), width: int = Form(...), height: int = Form(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "File must be an image.")
    
    content = await file.read()
    try:
        img = Image.open(BytesIO(content))
        # Use Lanczos for high-quality downsampling
        img = img.resize((width, height), Image.Resampling.LANCZOS)
        
        out_io = BytesIO()
        
        # Save in the original format if possible, otherwise PNG
        format = img.format if img.format else "PNG"
        if format == "JPEG" and img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
            
        img.save(out_io, format=format)
        
        return Response(
            content=out_io.getvalue(), 
            media_type=file.content_type, 
            headers={"Content-Disposition": f"attachment; filename=resized_{file.filename}"}
        )
    except Exception as e:
        raise HTTPException(500, f"Error resizing image: {str(e)}")

@router.post("/compress-pdf")
async def compress_pdf(file: UploadFile = File(...)):
    if file.content_type != "application/pdf" and not file.filename.endswith(".pdf"):
        raise HTTPException(400, "File must be a PDF.")
    
    content = await file.read()
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
        writer.remove_images(ignore_byte_string_object=True)
        writer.write(out_io)
        
        return Response(
            content=out_io.getvalue(), 
            media_type="application/pdf", 
            headers={"Content-Disposition": f"attachment; filename=compressed_{file.filename}"}
        )
    except Exception as e:
        raise HTTPException(500, f"Error processing PDF: {str(e)}")
