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
    # Startup: Initialize Database tables
    logger.info("Initializing database tables...")
    init_db()
    
    # Initialize Neo4j connection
    logger.info("Checking Neo4j connection...")
    neo4j_client.connect()

    # Seed default Admin and Investigator users if empty
    db = SessionLocal()
    try:
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            logger.info("Seeding initial admin and investigator users...")
            admin = User(
                username="admin",
                email="admin@forensics.local",
                hashed_password=get_password_hash("Admin123!"),
                full_name="Lead Forensic Administrator",
                role=UserRole.ADMIN,
                is_active=True
            )
            investigator = User(
                username="investigator",
                email="investigator@forensics.local",
                hashed_password=get_password_hash("Investigator123!"),
                full_name="Senior Digital Investigator",
                role=UserRole.INVESTIGATOR,
                is_active=True
            )
            viewer = User(
                username="viewer",
                email="viewer@forensics.local",
                hashed_password=get_password_hash("Viewer123!"),
                full_name="Case Auditor / Viewer",
                role=UserRole.VIEWER,
                is_active=True
            )
            db.add_all([admin, investigator, viewer])
            db.commit()
            logger.info("Initial users seeded successfully (admin/Admin123!, investigator/Investigator123!, viewer/Viewer123!).")

        # Seed initial Case (CASE-001) if no cases exist
        from app.models.case import Case, CaseStatus
        existing_case = db.query(Case).first()
        if not existing_case:
            inv_user = db.query(User).filter(User.username == "investigator").first()
            default_case = Case(
                case_number="CASE-001",
                case_name="Insider Threat & Financial Exfiltration Investigation",
                description="Digital forensics investigation regarding unauthorized credential usage, sensitive data exfiltration, and anti-forensics timestamp manipulation on corporate workstations.",
                status=CaseStatus.IN_PROGRESS,
                created_by=inv_user.id if inv_user else None
            )
            db.add(default_case)
            db.commit()
            logger.info("Default case CASE-001 seeded successfully.")
    except Exception as e:
        logger.error(f"Error seeding default users or case: {e}")
    finally:
        db.close()

    yield

    # Shutdown
    logger.info("Shutting down application...")
    neo4j_client.close()

app = FastAPI(
    title="AI Forensics Timeline Reconstruction API",
    description="Backend and Database Foundation for Digital Forensic Timeline Reconstruction, Real Gap Calculation, Contradiction Detection, and Investigative Recommendations.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Configure CORS
cors_env = os.getenv("CORS_ORIGINS", "")
origins = []
if cors_env:
    try:
        parsed = json.loads(cors_env)
        if isinstance(parsed, list):
            origins = parsed
        else:
            origins = [str(parsed)]
    except Exception:
        origins = [o.strip() for o in cors_env.split(",") if o.strip()]

if not origins:
    origins = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

# Allow any onrender.com subdomain and local development origins by regex
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https://.*\.onrender\.com|http://(localhost|127\.0\.0\.1):\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routes
app.include_router(api_router)

@app.get("/health", tags=["System"])
def health_check():
    """System health check endpoint."""
    return {
        "status": "healthy",
        "service": "AI Forensics Timeline Reconstruction Backend",
        "database": "connected",
        "neo4j": "connected" if neo4j_client.is_available else "offline (resilient fallback active)"
    }
