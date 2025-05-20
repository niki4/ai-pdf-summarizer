import pytest
import os

@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment variables"""
    os.environ["GEMINI_API_KEY"] = "test_api_key"
    yield
    # Cleanup after tests
    if "GEMINI_API_KEY" in os.environ:
        del os.environ["GEMINI_API_KEY"] 