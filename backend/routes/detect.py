"""
Detection API routes — handles all detection endpoints.
"""
import json
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import JSONResponse
import time
from collections import defaultdict
from backend.services.gemini import analyze_content
from backend.services.scraper import scrape_url
from backend.database.db import save_scan, get_history, get_scan_by_id, delete_scan

router = APIRouter(prefix="/api", tags=["detection"])

# Simple in-memory rate limiter (IP -> [timestamps])
RATE_LIMIT = 10
RATE_WINDOW = 60 # seconds
ip_requests = defaultdict(list)

def check_rate_limit(request: Request):
    ip = request.client.host if request.client else "unknown"
    now = time.time()
    
    # Filter out requests older than the window
    ip_requests[ip] = [ts for ts in ip_requests[ip] if now - ts < RATE_WINDOW]
    
    if len(ip_requests[ip]) >= RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Rate limit exceeded (10 req/min). Please wait.")
        
    ip_requests[ip].append(now)

@router.post("/detect/text")
async def detect_text(
    request: Request,
    text: str = Form(...),
    detection_type: str = Form(...)
):
    check_rate_limit(request)
    """Analyze plain text input."""
    if len(text.strip()) < 20:
        raise HTTPException(status_code=400, detail="Text too short. Please provide at least 20 characters.")

    try:
        result = await analyze_content(text, detection_type)
        scan_id = save_scan(detection_type, text[:200], "text", result)
        result["id"] = scan_id
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/detect/url")
async def detect_url(
    request: Request,
    url: str = Form(...),
    detection_type: str = Form(...)
):
    check_rate_limit(request)
    """Scrape and analyze a URL."""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    scraped = await scrape_url(url)
    if not scraped.get("success"):
        raise HTTPException(status_code=400, detail=f"Could not fetch URL: {scraped.get('error')}")

    combined = f"Title: {scraped['title']}\n\nDescription: {scraped['meta_description']}\n\nContent:\n{scraped['content']}"
    try:
        result = await analyze_content(combined, detection_type)
        result["source_url"] = url
        result["page_title"] = scraped["title"]
        scan_id = save_scan(detection_type, f"URL: {url}", "url", result)
        result["id"] = scan_id
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/detect/file")
async def detect_file(
    request: Request,
    file: UploadFile = File(...),
    detection_type: str = Form(...)
):
    check_rate_limit(request)
    """Analyze an uploaded file (txt, pdf, docx)."""
    allowed_types = [
        "text/plain",
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ]

    content_bytes = await file.read()

    # Handle text files directly
    if file.content_type == "text/plain" or file.filename.endswith(".txt"):
        try:
            text = content_bytes.decode("utf-8")
        except UnicodeDecodeError:
            text = content_bytes.decode("latin-1")

    # Handle PDF files
    elif file.filename.endswith(".pdf"):
        try:
            import io
            try:
                import pypdf
                reader = pypdf.PdfReader(io.BytesIO(content_bytes))
                text = "\n".join(page.extract_text() or "" for page in reader.pages)
            except ImportError:
                raise HTTPException(status_code=400, detail="PDF support requires pypdf. Run: pip install pypdf")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Could not read PDF: {str(e)}")

    # Handle DOCX files
    elif file.filename.endswith(".docx"):
        try:
            import io
            try:
                from docx import Document
                doc = Document(io.BytesIO(content_bytes))
                text = "\n".join(para.text for para in doc.paragraphs)
            except ImportError:
                raise HTTPException(status_code=400, detail="DOCX support requires python-docx. Run: pip install python-docx")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Could not read DOCX: {str(e)}")

    else:
        # Try to decode as text anyway
        try:
            text = content_bytes.decode("utf-8")
        except Exception:
            raise HTTPException(status_code=400, detail="Unsupported file type. Use .txt, .pdf, or .docx")

    if len(text.strip()) < 20:
        raise HTTPException(status_code=400, detail="File content too short or empty.")

    try:
        result = await analyze_content(text, detection_type)
        result["source_filename"] = file.filename
        scan_id = save_scan(detection_type, f"File: {file.filename}", "file", result)
        result["id"] = scan_id
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/history")
async def get_scan_history(limit: int = 50):
    """Get scan history."""
    history = get_history(limit)
    return JSONResponse(content={"scans": history})


@router.get("/history/{scan_id}")
async def get_single_scan(scan_id: int):
    """Get a single scan result."""
    scan = get_scan_by_id(scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found.")
    return JSONResponse(content=scan)


@router.delete("/history/{scan_id}")
async def delete_scan_record(scan_id: int):
    """Delete a scan from history."""
    delete_scan(scan_id)
    return JSONResponse(content={"message": "Scan deleted successfully."})
