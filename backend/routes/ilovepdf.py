import os
import zipfile
import tempfile
from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import Response, FileResponse
from io import BytesIO
from pypdf import PdfReader, PdfWriter
import fitz  # PyMuPDF
from pdf2docx import Converter

router = APIRouter(prefix="/api/ilovepdf", tags=["iLovePDF Tools"])

MAX_FILE_SIZE = 50 * 1024 * 1024

@router.post("/compress")
async def compress_pdf(file: UploadFile = File(...)):
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(400, "File too large (max 50MB).")
    if file.content_type != "application/pdf" and not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "File must be a PDF.")
    
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
            headers={"Content-Disposition": f"attachment; filename=compressed_{file.filename}"}
        )
    except Exception as e:
        raise HTTPException(500, f"Error processing PDF: {str(e)}")

@router.post("/merge")
async def merge_pdfs(files: list[UploadFile] = File(...)):
    writer = PdfWriter()
    for file in files:
        if file.content_type != "application/pdf" and not file.filename.lower().endswith('.pdf'):
            continue
        content = await file.read()
        reader = PdfReader(BytesIO(content))
        for page in reader.pages:
            writer.add_page(page)
    
    out_io = BytesIO()
    writer.write(out_io)
    return Response(
        content=out_io.getvalue(), 
        media_type="application/pdf", 
        headers={"Content-Disposition": "attachment; filename=merged.pdf"}
    )

@router.post("/split")
async def split_pdf(file: UploadFile = File(...), ranges: str = Form(...)):
    # ranges format: "1-3,5,7-10" (1-indexed)
    content = await file.read()
    reader = PdfReader(BytesIO(content))
    writer = PdfWriter()
    
    try:
        pages_to_keep = set()
        for part in ranges.split(','):
            if '-' in part:
                start, end = part.split('-')
                pages_to_keep.update(range(int(start)-1, int(end)))
            else:
                pages_to_keep.add(int(part)-1)
                
        for i, page in enumerate(reader.pages):
            if i in pages_to_keep:
                writer.add_page(page)
                
        out_io = BytesIO()
        writer.write(out_io)
        return Response(
            content=out_io.getvalue(), 
            media_type="application/pdf", 
            headers={"Content-Disposition": f"attachment; filename=split_{file.filename}"}
        )
    except Exception as e:
        raise HTTPException(400, f"Invalid range format. Use e.g. 1-3,5. Error: {str(e)}")

@router.post("/pdf-to-word")
async def pdf_to_word(file: UploadFile = File(...)):
    content = await file.read()
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        tmp_pdf.write(content)
        tmp_pdf_path = tmp_pdf.name
        
    tmp_docx_path = tmp_pdf_path.replace(".pdf", ".docx")
    
    try:
        cv = Converter(tmp_pdf_path)
        cv.convert(tmp_docx_path, start=0, end=None)
        cv.close()
        
        with open(tmp_docx_path, "rb") as f:
            docx_data = f.read()
            
        return Response(
            content=docx_data,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename={file.filename.replace('.pdf', '.docx')}"}
        )
    finally:
        if os.path.exists(tmp_pdf_path): os.remove(tmp_pdf_path)
        if os.path.exists(tmp_docx_path): os.remove(tmp_docx_path)

@router.post("/pdf-to-image")
async def pdf_to_image(file: UploadFile = File(...)):
    content = await file.read()
    
    # Use PyMuPDF to render pages
    doc = fitz.open(stream=content, filetype="pdf")
    
    out_zip_io = BytesIO()
    with zipfile.ZipFile(out_zip_io, "w", zipfile.ZIP_DEFLATED) as zf:
        for i in range(len(doc)):
            page = doc.load_page(i)
            pix = page.get_pixmap(dpi=150)
            img_data = pix.tobytes("jpeg")
            zf.writestr(f"page_{i+1}.jpg", img_data)
            
    doc.close()
    
    return Response(
        content=out_zip_io.getvalue(),
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={file.filename}_images.zip"}
    )

@router.post("/protect")
async def protect_pdf(file: UploadFile = File(...), password: str = Form(...)):
    content = await file.read()
    reader = PdfReader(BytesIO(content))
    writer = PdfWriter()
    
    for page in reader.pages:
        writer.add_page(page)
        
    writer.encrypt(password)
    out_io = BytesIO()
    writer.write(out_io)
    
    return Response(
        content=out_io.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=protected_{file.filename}"}
    )

@router.post("/unlock")
async def unlock_pdf(file: UploadFile = File(...), password: str = Form(...)):
    content = await file.read()
    reader = PdfReader(BytesIO(content))
    
    if reader.is_encrypted:
        success = reader.decrypt(password)
        if success == 0:
            raise HTTPException(401, "Invalid password")
            
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
        
    out_io = BytesIO()
    writer.write(out_io)
    
    return Response(
        content=out_io.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=unlocked_{file.filename}"}
    )

@router.post("/rotate")
async def rotate_pdf(file: UploadFile = File(...), angle: int = Form(...)):
    # angle should be 90, 180, 270
    content = await file.read()
    reader = PdfReader(BytesIO(content))
    writer = PdfWriter()
    
    for page in reader.pages:
        page.rotate(angle)
        writer.add_page(page)
        
    out_io = BytesIO()
    writer.write(out_io)
    
    return Response(
        content=out_io.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=rotated_{file.filename}"}
    )

@router.post("/remove-pages")
async def remove_pages(file: UploadFile = File(...), pages: str = Form(...)):
    # pages to remove e.g. "1,3,5" (1-indexed)
    content = await file.read()
    reader = PdfReader(BytesIO(content))
    writer = PdfWriter()
    
    try:
        pages_to_remove = {int(p)-1 for p in pages.split(',')}
        for i, page in enumerate(reader.pages):
            if i not in pages_to_remove:
                writer.add_page(page)
                
        out_io = BytesIO()
        writer.write(out_io)
        return Response(
            content=out_io.getvalue(), 
            media_type="application/pdf", 
            headers={"Content-Disposition": f"attachment; filename=cleaned_{file.filename}"}
        )
    except Exception as e:
        raise HTTPException(400, "Invalid pages format. Use e.g. 1,3,5")

from PIL import Image

@router.post("/image-to-pdf")
async def image_to_pdf(files: list[UploadFile] = File(...)):
    images = []
    for f in files:
        if f.content_type.startswith("image/"):
            content = await f.read()
            img = Image.open(BytesIO(content))
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            images.append(img)
            
    if not images:
        raise HTTPException(400, "No valid images provided")
        
    out_io = BytesIO()
    images[0].save(out_io, format="PDF", save_all=True, append_images=images[1:])
    
    return Response(
        content=out_io.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=converted_images.pdf"}
    )

@router.post("/extract-text")
async def extract_text(file: UploadFile = File(...)):
    content = await file.read()
    reader = PdfReader(BytesIO(content))
    text = ""
    for i, page in enumerate(reader.pages):
        page_text = page.extract_text()
        if page_text:
            text += f"--- Page {i+1} ---\n{page_text}\n\n"
            
    return Response(
        content=text.encode("utf-8"),
        media_type="text/plain",
        headers={"Content-Disposition": f"attachment; filename=extracted_{file.filename}.txt"}
    )

@router.post("/pdf-to-html")
async def pdf_to_html(file: UploadFile = File(...)):
    content = await file.read()
    doc = fitz.open(stream=content, filetype="pdf")
    html_out = "<html><head><meta charset='utf-8'></head><body>"
    
    for i in range(len(doc)):
        page = doc.load_page(i)
        html_out += page.get_text("html")
        html_out += "<hr>"
        
    html_out += "</body></html>"
    doc.close()
    
    return Response(
        content=html_out.encode("utf-8"),
        media_type="text/html",
        headers={"Content-Disposition": f"attachment; filename={file.filename}.html"}
    )

@router.post("/organize")
async def organize_pdf(file: UploadFile = File(...), order: str = Form(...)):
    # order e.g. "5,1,2,4"
    content = await file.read()
    reader = PdfReader(BytesIO(content))
    writer = PdfWriter()
    
    try:
        page_indices = [int(p)-1 for p in order.split(',')]
        for i in page_indices:
            writer.add_page(reader.pages[i])
            
        out_io = BytesIO()
        writer.write(out_io)
        return Response(
            content=out_io.getvalue(), 
            media_type="application/pdf", 
            headers={"Content-Disposition": f"attachment; filename=organized_{file.filename}"}
        )
    except Exception as e:
        raise HTTPException(400, f"Invalid order format. Use e.g. 5,1,2,4. Error: {str(e)}")

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

@router.post("/add-watermark")
async def add_watermark(file: UploadFile = File(...), text: str = Form(...)):
    content = await file.read()
    reader = PdfReader(BytesIO(content))
    writer = PdfWriter()
    
    # Create a simple watermark PDF using reportlab
    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    can.setFont("Helvetica", 60)
    can.setFillColorRGB(0.5, 0.5, 0.5, alpha=0.3)
    can.saveState()
    can.translate(300, 400)
    can.rotate(45)
    can.drawCentredString(0, 0, text)
    can.restoreState()
    can.save()
    packet.seek(0)
    
    watermark_pdf = PdfReader(packet)
    watermark_page = watermark_pdf.pages[0]
    
    for page in reader.pages:
        page.merge_page(watermark_page)
        writer.add_page(page)
        
    out_io = BytesIO()
    writer.write(out_io)
    
    return Response(
        content=out_io.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=watermarked_{file.filename}"}
    )

