"""
Honeypot Agent API - Main Application
FastAPI application for detecting and engaging with scammers.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api import endpoints

# --- LIFESPAN MANAGEMENT ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    print("🚀 Honeypot Agent API Starting...")
    print("✅ Ready to engage scammers!")
    yield
    # Shutdown
    print("👋 Honeypot Agent API Shutting down...")

# Initialize the FastAPI Application
app = FastAPI(
    title="Honeypot Agent API",
    description="AI-driven honeypot for detecting and engaging scammers",
    version="2.0.0",
    lifespan=lifespan
)

# CORS Middleware - Allow connections from anywhere
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routes
app.include_router(endpoints.router, prefix="/api/v1")

# Root Health Check
@app.get("/")
def root():
    return {
        "status": "running",
        "service": "Honeypot Agent API",
        "version": "2.0.0",
        "endpoints": {
            "chat": "/api/v1/chat",
            "health": "/api/v1/health"
        }
    }

# Run the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
