import os
import zipfile
import tempfile
from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import Response
from io import BytesIO
import fitz  # PyMuPDF
from pdf2docx import Converter
from PIL import Image

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
        doc = fitz.open(stream=content, filetype="pdf")
        out_io = BytesIO()
        doc.save(out_io, garbage=4, deflate=True, clean=True)
        doc.close()
        return Response(content=out_io.getvalue(), media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=compressed_{file.filename}"})
    except Exception as e:
        raise HTTPException(500, f"Error processing PDF: {str(e)}")

@router.post("/merge")
async def merge_pdfs(files: list[UploadFile] = File(...)):
    out_doc = fitz.open()
    for file in files:
        if file.content_type == "application/pdf" or file.filename.lower().endswith('.pdf'):
            content = await file.read()
            doc = fitz.open(stream=content, filetype="pdf")
            out_doc.insert_pdf(doc)
            doc.close()
    
    out_io = BytesIO()
    out_doc.save(out_io)
    out_doc.close()
    return Response(content=out_io.getvalue(), media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=merged.pdf"})

@router.post("/split")
async def split_pdf(file: UploadFile = File(...), ranges: str = Form(...)):
    content = await file.read()
    doc = fitz.open(stream=content, filetype="pdf")
    out_doc = fitz.open()
    
    try:
        pages_to_keep = set()
        for part in ranges.split(','):
            if '-' in part:
                start, end = part.split('-')
                pages_to_keep.update(range(int(start)-1, int(end)))
            else:
                pages_to_keep.add(int(part)-1)
                
        for i in sorted(pages_to_keep):
            if 0 <= i < len(doc):
                out_doc.insert_pdf(doc, from_page=i, to_page=i)
                
        out_io = BytesIO()
        out_doc.save(out_io)
        out_doc.close()
        doc.close()
        return Response(content=out_io.getvalue(), media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=split_{file.filename}"})
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
    doc = fitz.open(stream=content, filetype="pdf")
    out_io = BytesIO()
    doc.save(out_io, encryption=fitz.PDF_ENCRYPT_AES_256, user_pw=password, owner_pw=password)
    doc.close()
    
    return Response(
        content=out_io.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=protected_{file.filename}"}
    )

@router.post("/unlock")
async def unlock_pdf(file: UploadFile = File(...), password: str = Form(...)):
    content = await file.read()
    doc = fitz.open(stream=content, filetype="pdf")
    
    if doc.is_encrypted:
        if not doc.authenticate(password):
            raise HTTPException(401, "Invalid password")
            
    out_io = BytesIO()
    doc.save(out_io)
    doc.close()
    
    return Response(
        content=out_io.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=unlocked_{file.filename}"}
    )

@router.post("/rotate")
async def rotate_pdf(file: UploadFile = File(...), angle: int = Form(...)):
    content = await file.read()
    doc = fitz.open(stream=content, filetype="pdf")
    
    for page in doc:
        page.set_rotation(page.rotation + angle)
        
    out_io = BytesIO()
    doc.save(out_io)
    doc.close()
    
    return Response(
        content=out_io.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=rotated_{file.filename}"}
    )

@router.post("/remove-pages")
async def remove_pages(file: UploadFile = File(...), pages: str = Form(...)):
    content = await file.read()
    doc = fitz.open(stream=content, filetype="pdf")
    
    try:
        pages_to_remove = sorted([int(p)-1 for p in pages.split(',')], reverse=True)
        for p in pages_to_remove:
            if 0 <= p < len(doc):
                doc.delete_page(p)
                
        out_io = BytesIO()
        doc.save(out_io)
        doc.close()
        return Response(content=out_io.getvalue(), media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=cleaned_{file.filename}"})
    except Exception:
        raise HTTPException(400, "Invalid pages format. Use e.g. 1,3,5")

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
    doc = fitz.open(stream=content, filetype="pdf")
    text = ""
    for i, page in enumerate(doc):
        page_text = page.get_text()
        if page_text:
            text += f"--- Page {i+1} ---\n{page_text}\n\n"
            
    doc.close()
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
    content = await file.read()
    doc = fitz.open(stream=content, filetype="pdf")
    out_doc = fitz.open()
    
    try:
        page_indices = [int(p)-1 for p in order.split(',')]
        for i in page_indices:
            if 0 <= i < len(doc):
                out_doc.insert_pdf(doc, from_page=i, to_page=i)
                
        out_io = BytesIO()
        out_doc.save(out_io)
        out_doc.close()
        doc.close()
        return Response(content=out_io.getvalue(), media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=organized_{file.filename}"})
    except Exception as e:
        raise HTTPException(400, f"Invalid order format. Use e.g. 5,1,2,4. Error: {str(e)}")

@router.post("/add-watermark")
async def add_watermark(file: UploadFile = File(...), text: str = Form(...)):
    content = await file.read()
    doc = fitz.open(stream=content, filetype="pdf")
    
    for page in doc:
        rect = page.rect
        page.insert_text(fitz.Point(rect.width/2 - 50, rect.height/2), text, fontsize=60, color=(0.5, 0.5, 0.5), fill_opacity=0.3, rotate=45)
        
    out_io = BytesIO()
    doc.save(out_io)
    doc.close()
    
    return Response(
        content=out_io.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=watermarked_{file.filename}"}
    )
