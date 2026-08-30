import pytest
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database.base import Base
from app.database.session import get_db
from app.main import app
from app.models.user import User, UserRole
from app.auth.security import get_password_hash
from app.auth.jwt import create_access_token

# Use in-memory SQLite with StaticPool so all connections share the same memory instance
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine_test = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)

@pytest.fixture(autouse=True)
def init_test_database():
    """Create all tables before each test and drop them after."""
    Base.metadata.create_all(bind=engine_test)
    yield
    Base.metadata.drop_all(bind=engine_test)

@pytest.fixture
def db_session():
    """Yields a database session."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def client():
    """FastAPI TestClient with overridden get_db dependency."""
    def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def admin_user(db_session) -> User:
    user = User(
        username="admin_test",
        email="admin_test@forensics.local",
        hashed_password=get_password_hash("AdminPass123!"),
        full_name="Test Administrator",
        role=UserRole.ADMIN,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def investigator_user(db_session) -> User:
    user = User(
        username="investigator_test",
        email="investigator_test@forensics.local",
        hashed_password=get_password_hash("InvestigatorPass123!"),
        full_name="Test Investigator",
        role=UserRole.INVESTIGATOR,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def viewer_user(db_session) -> User:
    user = User(
        username="viewer_test",
        email="viewer_test@forensics.local",
        hashed_password=get_password_hash("ViewerPass123!"),
        full_name="Test Viewer",
        role=UserRole.VIEWER,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def investigator_token(investigator_user) -> str:
    return create_access_token({"sub": str(investigator_user.id), "username": investigator_user.username, "role": "Investigator"})

@pytest.fixture
def admin_token(admin_user) -> str:
    return create_access_token({"sub": str(admin_user.id), "username": admin_user.username, "role": "Admin"})

@pytest.fixture
def viewer_token(viewer_user) -> str:
    return create_access_token({"sub": str(viewer_user.id), "username": viewer_user.username, "role": "Viewer"})
