"""Main FastAPI application entry point."""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.config.settings import settings

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development
        "http://127.0.0.1:3000",  # Local development via 127.0.0.1
        "http://0.0.0.0:3000",  # Docker/local network access
        "https://localhost:3000",  # HTTPS localhost (dev certs)
        "http://localhost:3001",  # Alternative local port
        "http://127.0.0.1:3001",  # Alternative local port via 127.0.0.1
        "https://lattice-2ulsedyha-aryamangoenkas-projects.vercel.app",  # Vercel deployment
        "https://lattice-rose.vercel.app",  # Vercel production domain
        "https://lattice-aryamangoenkas-projects.vercel.app",  # Vercel alias
        "https://frontend-mka120fwe-aryamangoenkas-projects.vercel.app",  # Previous deployment
        "https://frontend-n2tazkq5v-aryamangoenkas-projects.vercel.app",  # Latest deployment
        "https://frontend-omega-sepia-46.vercel.app",  # Production domain
        "https://frontend-aryamangoenkas-projects.vercel.app",  # Frontend production domain
        "https://e5e88adea615.ngrok-free.app",  # ngrok tunnel
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*", "ngrok-skip-browser-warning"],
    expose_headers=["*"],
)


# Add logging middleware for debugging CORS issues
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests to debug CORS issues."""
    origin = request.headers.get("origin", "No Origin")
    method = request.method
    path = request.url.path
    
    logger.debug(f"🌐 Request: {method} {path} from origin: {origin}")
    
    response = await call_next(request)
    return response


@app.on_event("startup")
async def startup_event() -> None:
    """Run on application startup."""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Run on application shutdown."""
    logger.info("Shutting down application")


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {
        "message": "Lattice Backend API",
        "version": settings.APP_VERSION,
        "status": "running",
    }


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


# Import and include routers
from app.api import accounts, auth, chats, groups, insights, onboarding, transactions
from app.api import settings as settings_router

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(onboarding.router, prefix="/api/onboarding", tags=["Onboarding"])
app.include_router(chats.router, prefix="/api/chats", tags=["Chats"])
app.include_router(groups.router, prefix="/api/groups", tags=["Groups"])
app.include_router(accounts.router, prefix="/api/accounts", tags=["Accounts"])
app.include_router(transactions.router, prefix="/api/transactions", tags=["Transactions"])
app.include_router(insights.router, prefix="/api/insights", tags=["Insights"])
app.include_router(settings_router.router, prefix="/api/settings", tags=["Settings"])

