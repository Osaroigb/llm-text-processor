import uvicorn
from fastapi import FastAPI
from fastapi.responses import Response
from app.core.db import close_db, init_db
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from app.schemas import HomeResponse, HealthResponse
from app.api.routes import router as analysis_router
from app.core import get_settings, setup_logging, get_logger

# Get settings and setup logging
settings = get_settings()
setup_logging(settings)
logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application lifespan events."""    
    try:
        logger.info("Initializing database connection...")
        await init_db()
        logger.info("Database connection established successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
    
    yield
    await close_db()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION,
    docs_url="/docs",
    redoc_url=None,
    swagger_ui_parameters={
        "displayRequestDuration": True,
    },
    debug=settings.DEBUG,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(analysis_router)

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204)

@app.get("/", response_model=HomeResponse)
async def home():
    """Root endpoint with basic info."""
    return {
        "message": "LLM Text Processor API",
        "version": "0.1.0",
        "status": "running"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "service": "llm-text-processor",
        "version": "0.1.0"
    }

if __name__ == "__main__":
    logger.info(f"Starting server on {settings.APP_HOST}:{settings.APP_PORT}")
    uvicorn.run(
        app, 
        host=settings.APP_HOST, 
        port=settings.APP_PORT,
        log_level=settings.LOG_LEVEL.lower(),
        reload=settings.APP_RELOAD
    )
