from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict
from .config import ALLOWED_ORIGINS

app = FastAPI(
    title="Computer Vision API",
    description="API for managing computer vision cameras and streams",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint"""
    return {"status": "healthy"}

# Import and include routers
from .routes import cameras
app.include_router(cameras.router, prefix="/api/v1", tags=["Cameras"])

# Import and include routers
from .routes import auth
app.include_router(auth.router, prefix="/api/v1", tags=["Authentication"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)