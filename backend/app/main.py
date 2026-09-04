import os
import json
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router
from app.database.session import init_db, SessionLocal
from app.models.user import User, UserRole
from app.auth.security import get_password_hash
from app.graph.neo4j_client import neo4j_client
from app.utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ---------------------------------------
    # Startup: Initialize Database
    # ---------------------------------------
    logger.info("Initializing database tables...")
    init_db()

    # ---------------------------------------
    # Initialize Neo4j connection
    # ---------------------------------------
    logger.info("Checking Neo4j connection...")
    neo4j_client.connect()

    # ---------------------------------------
    # Seed default users
    # ---------------------------------------
    db = SessionLocal()

    try:
        admin_user = (
            db.query(User)
            .filter(User.username == "admin")
            .first()
        )

        if not admin_user:
            logger.info(
                "Seeding initial admin and investigator users..."
            )

            admin = User(
                username="admin",
                email="admin@forensics.local",
                hashed_password=get_password_hash("Admin123!"),
                full_name="Lead Forensic Administrator",
                role=UserRole.ADMIN,
                is_active=True,
            )

            investigator = User(
                username="investigator",
                email="investigator@forensics.local",
                hashed_password=get_password_hash(
                    "Investigator123!"
                ),
                full_name="Senior Digital Investigator",
                role=UserRole.INVESTIGATOR,
                is_active=True,
            )

            viewer = User(
                username="viewer",
                email="viewer@forensics.local",
                hashed_password=get_password_hash("Viewer123!"),
                full_name="Case Auditor / Viewer",
                role=UserRole.VIEWER,
                is_active=True,
            )

            db.add_all([
                admin,
                investigator,
                viewer,
            ])

            db.commit()

            logger.info(
                "Initial users seeded successfully "
                "(admin/Admin123!, "
                "investigator/Investigator123!, "
                "viewer/Viewer123!)."
            )

        # ---------------------------------------
        # Seed baseline forensic case (CASE-001)
        # ---------------------------------------
        try:
            from app.database.seed import seed_initial_demo_case
            seed_initial_demo_case(db)
        except Exception as seed_err:
            logger.warning(f"Demo case auto-seeding encountered warning: {seed_err}")

    except Exception as e:
        logger.error(
            f"Error seeding default users: {e}"
        )

    finally:
        db.close()

    yield

    # ---------------------------------------
    # Shutdown
    # ---------------------------------------
    logger.info("Shutting down application...")
    neo4j_client.close()


# ==========================================
# FastAPI Application
# ==========================================

app = FastAPI(
    title="AI Forensics Timeline Reconstruction API",
    description=(
        "Backend and Database Foundation for Digital "
        "Forensic Timeline Reconstruction, Real Gap "
        "Calculation, Contradiction Detection, and "
        "Investigative Recommendations."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)


# ==========================================
# CORS CONFIGURATION (Render & Global Ready)
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# API ROUTES
# ==========================================

app.include_router(api_router)


# ==========================================
# HEALTH CHECK
# ==========================================

@app.get("/health", tags=["System"])
def health_check():
    """
    System health check endpoint.
    """
    return {
        "status": "healthy",
        "service": "AI Forensics Timeline Reconstruction Backend",
        "database": "connected",
        "neo4j": (
            "connected"
            if neo4j_client.is_available
            else "offline (resilient fallback active)"
        ),
    }


# ==========================================
# FRONTEND SPA STATIC HOSTING (RENDER / PROD)
# ==========================================

from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from fastapi import HTTPException

def get_frontend_dist():
    possible_dist_dirs = [
        Path(__file__).resolve().parent.parent.parent / "frontend" / "dist",
        Path(__file__).resolve().parent.parent / "frontend" / "dist",
        Path("./frontend/dist").resolve(),
        Path("../frontend/dist").resolve(),
        Path("./dist").resolve(),
    ]
    for d in possible_dist_dirs:
        if d.exists() and (d / "index.html").exists():
            return d
    return None

# Mount /assets directly using StaticFiles for high-performance, strict MIME handling
_dist_dir = get_frontend_dist()
if _dist_dir and (_dist_dir / "assets").is_dir():
    app.mount("/assets", StaticFiles(directory=str(_dist_dir / "assets")), name="assets")

@app.get("/{full_path:path}", include_in_schema=False)
async def serve_spa_frontend(full_path: str):
    # Don't intercept API, documentation, or health check routes
    if (
        full_path == "api"
        or full_path.startswith("api/")
        or full_path in ["docs", "redoc", "openapi.json", "health"]
    ):
        raise HTTPException(status_code=404, detail="Not Found")

    dist = get_frontend_dist()
    if not dist:
        return HTMLResponse(
            "<html><body style='font-family:sans-serif;padding:40px;text-align:center;background:#0f172a;color:#f8fafc;'>"
            "<h2 style='color:#38bdf8;'>AI Forensics Timeline Reconstruction Backend</h2>"
            "<p>API service is healthy and active. Explore interactive documentation at <a style='color:#60a5fa;' href='/docs'>/docs</a>.</p>"
            "</body></html>"
        )

    target_file = dist / full_path
    if full_path and target_file.is_file():
        media_type = None
        if full_path.endswith((".js", ".mjs")):
            media_type = "application/javascript"
        elif full_path.endswith(".css"):
            media_type = "text/css"
        elif full_path.endswith(".svg"):
            media_type = "image/svg+xml"
        elif full_path.endswith(".json"):
            media_type = "application/json"
        elif full_path.endswith(".png"):
            media_type = "image/png"
        elif full_path.endswith((".jpg", ".jpeg")):
            media_type = "image/jpeg"
        return FileResponse(target_file, media_type=media_type)

    return FileResponse(dist / "index.html", media_type="text/html")