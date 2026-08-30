from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

app = FastAPI(
    title="Short Link Service",
    description="A simple URL shortener using FastAPI.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.get(
    "/health",
    summary="Service Health Check",
    description="Returns the health status of the service.",
    status_code=status.HTTP_200_OK
)
async def health_check():
    """
    Health endpoint to verify the service is running.
    Since we have no database, it always returns healthy.
    """
    return JSONResponse(
        content={
            "status": "healthy",
            "storage": "in-memory (volatile)",
            "service": "Short Link Service is running smoothly."
        },
        status_code=status.HTTP_200_OK
    )

@app.get("/", summary="Welcome")
async def root():
    return {
        "message": "Welcome to the Short Link Service!",
        "docs": "/docs",
        "health_check": "/health",
        "warning": "All data will be lost on server restart (in-memory storage)."
    }
