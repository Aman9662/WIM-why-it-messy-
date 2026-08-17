"""
Why It's Messy — FastAPI Backend Entry Point
"""
import os
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv

from backend.routes.detect import router as detect_router
from backend.routes.utilities import router as utils_router
from backend.routes.ilovepdf import router as ilovepdf_router
from backend.routes.transfer import router as transfer_router
from backend.database.db import init_db, cleanup_expired_transfers_db

# Load .env at the top level so all modules can read env vars
load_dotenv()


async def cleanup_task():
    """Background task to delete expired transfer files every 5 minutes."""
    while True:
        try:
            await asyncio.sleep(300)  # 5 minutes
            expired_files = cleanup_expired_transfers_db()
            for path in expired_files:
                if os.path.exists(path):
                    try:
                        os.remove(path)
                        print(f"Cleaned up expired transfer: {path}")
                    except OSError:
                        pass
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"Cleanup error: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: init DB on startup, cancel cleanup on shutdown."""
    init_db()
    task = asyncio.create_task(cleanup_task())
    yield
    task.cancel()


app = FastAPI(
    title="Why It's Messy API",
    description="The all-in-one utility platform — Detection, PDF Tools, Size Fixer, Transfer.",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

# CORS — allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API route groups
app.include_router(detect_router)
app.include_router(utils_router)
app.include_router(ilovepdf_router)
app.include_router(transfer_router)

# Serve frontend static files
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "frontend")
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "version": "1.0.0"}


@app.get("/", include_in_schema=False)
async def serve_home():
    path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(path):
        return FileResponse(path)
    return {"message": "API is running. Frontend not found."}


@app.get("/{page}", include_in_schema=False)
async def serve_page(page: str):
    # Guard: don't intercept API or static paths
    if page.startswith(("api", "static")):
        return {"error": "Not found"}, 404

    file_path = os.path.join(FRONTEND_DIR, f"{page}.html")
    if os.path.exists(file_path):
        return FileResponse(file_path)

    # Fallback to index for SPA-like behavior
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"error": "Page not found"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", 8000)),
        reload=True,
    )
