"""
pytest Configuration and Fixtures
"""
import pytest
import sys
import os
from unittest.mock import MagicMock

# Use SQLite for tests so database.py async engine uses aiosqlite (no Docker required)
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
# Disable cloud storage in tests so lifespan does not call initialize_buckets (override .env if present)
os.environ["USE_CLOUD_STORAGE"] = "false"
# Required by character_chat_service.ChatOpenAI at import time (no real API calls in tests)
os.environ.setdefault("OPENAI_API_KEY", "test-key-for-pytest")
# Wiro client / story service (no real API calls in tests)
os.environ.setdefault("WIRO_API_KEY", "test-key-for-pytest")

# Add backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock heavy/optional dependencies before importing the app (sentry_sdk not mocked so lifespan path stays real).
# Do NOT mock langchain/langchain_core: character_chat_service imports langchain_openai which needs real langchain_core.
mock_modules = [
    'google', 'google.genai', 'google.generativeai',
    'transformers', 'torch', 'diffusers', 'accelerate',
    'replicate', 'elevenlabs', 'gtts', 'pydub',
    'PIL', 'PIL.Image',
]
for mod in mock_modules:
    if mod not in sys.modules:
        sys.modules[mod] = MagicMock()

# Celery: need a real module tree so "from celery" and "from celery.utils.log" work
_celery_log = type(sys)("celery.utils.log")
_celery_log.get_task_logger = MagicMock()
_celery_utils = type(sys)("celery.utils")
_celery_utils.log = _celery_log
_celery = type(sys)("celery")
_celery.utils = _celery_utils
_celery.shared_task = MagicMock()
sys.modules["celery.utils.log"] = _celery_log
sys.modules["celery.utils"] = _celery_utils
sys.modules["celery"] = _celery

# Prevent Sentry init from running (avoids needing real sentry_sdk in path during import)
def _noop_init_sentry():
    pass
sys.modules.setdefault("app.core.sentry_config", type(sys)("app.core.sentry_config"))
sys.modules["app.core.sentry_config"].init_sentry = _noop_init_sentry
sys.modules["app.core.sentry_config"].capture_exception = lambda *a, **k: None

# pgvector is PostgreSQL-only; for SQLite tests use Text as placeholder
if "pgvector" not in sys.modules:
    from sqlalchemy import Text
    _pgvector_sqlalchemy = MagicMock()
    _pgvector_sqlalchemy.Vector = lambda dimension: Text()
    sys.modules["pgvector.sqlalchemy"] = _pgvector_sqlalchemy
    _pgvector = MagicMock()
    _pgvector.sqlalchemy = _pgvector_sqlalchemy
    sys.modules["pgvector"] = _pgvector

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import httpx
import uuid

# Now import app modules
try:
    from app.core.database import Base, get_db
    from app.core.config import settings
    from main import app

except ImportError as e:
    print(f"Warning: Could not import app modules: {e}")
    # Create minimal stubs for unit tests
    Base = MagicMock()
    get_db = MagicMock()
    app = MagicMock()


# Test database URL (use in-memory SQLite for speed)
TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    Base.metadata.create_all(bind=engine)
    
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database override. Uses httpx ASGITransport to avoid
    Starlette TestClient lifespan (which was hitting MagicMock in our mocked env)."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with httpx.Client(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver",
    ) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_client(client):
    """Alias for client (e.g. test_health.py uses test_client)."""
    return client


@pytest.fixture
def sample_user_id():
    """Generate a sample user ID"""
    return uuid.uuid4()


@pytest.fixture
def sample_story_data():
    """Sample story request data"""
    return {
        "theme": "Test story theme",
        "language": "tr",
        "story_type": "masal",
        "use_async": False
    }


@pytest.fixture
def mock_user():
    """Sample mock user data"""
    return {
        "id": str(uuid.uuid4()),
        "email": "test@example.com",
        "name": "Test User",
        "password_hash": "$2b$12$test_hash",  # bcrypt hash
        "email_verified": True,
        "is_active": True,
        "created_at": "2026-01-09T12:00:00",
        "subscription_tier": "free"
    }


@pytest.fixture
def mock_character_data():
    """Sample character creation data"""
    return {
        "name": "Test Character",
        "description": "A brave hero for testing",
        "traits": ["brave", "kind", "smart"],
        "age_group": "child",
        "gender": "neutral"
    }


@pytest.fixture
def mock_stripe_event():
    """Sample Stripe webhook event"""
    return {
        "id": "evt_test_123",
        "type": "payment_intent.succeeded",
        "data": {
            "object": {
                "id": "pi_test_123",
                "amount": 1999,
                "currency": "try",
                "status": "succeeded",
                "metadata": {
                    "user_id": "test_user_123",
                    "product_id": "credits_100",
                    "credits": 100
                }
            }
        },
        "created": 1704067200
    }


@pytest.fixture
def auth_headers():
    """Generate authenticated request headers"""
    # In real tests, this would use a valid JWT token
    return {
        "Authorization": "Bearer test_token_123",
        "Content-Type": "application/json"
    }


@pytest.fixture
def mock_gdpr_export_data():
    """Sample GDPR export data"""
    return {
        "user_profile": {
            "id": "user_123",
            "email": "test@example.com",
            "name": "Test User",
            "created_at": "2026-01-01T00:00:00"
        },
        "stories": [
            {"id": "story_1", "title": "Test Story", "created_at": "2026-01-02T00:00:00"}
        ],
        "characters": [],
        "achievements": [],
        "settings": {
            "analytics_enabled": True,
            "marketing_emails": False
        },
        "export_date": "2026-01-09T12:00:00"
    }


@pytest.fixture
def mock_privacy_settings():
    """Sample privacy settings"""
    return {
        "analytics_enabled": True,
        "marketing_emails": False,
        "share_reading_history": False,
        "third_party_sharing": False,
        "personalized_recommendations": True
    }


# Markers for test categorization
def pytest_configure(config):
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow tests")
    config.addinivalue_line("markers", "asyncio: Async tests")
