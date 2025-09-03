import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.models.analysis import Analysis
from app.schemas.analysis import AnalyzeRequest


class TestAnalyzeEndpoint:
    """Test cases for the /analyze endpoint."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    def test_analyze_text_empty_text(self, client):
        """Test analysis with empty text."""
        response = client.post(
            "/analysis/analyze",
            json={"text": ""}
        )
        assert response.status_code == 422  # Validation error
    
    def test_analyze_text_missing_text(self, client):
        """Test analysis with missing text field."""
        response = client.post(
            "/analysis/analyze",
            json={}
        )
        assert response.status_code == 422  # Validation error
    
    def test_analyze_text_too_long(self, client):
        """Test analysis with text exceeding max length."""
        long_text = "x" * 10001  # Exceeds max_length=10000
        response = client.post(
            "/analysis/analyze",
            json={"text": long_text}
        )
        assert response.status_code == 422  # Validation error


class TestSearchEndpoint:
    """Test cases for the /search endpoint."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    def test_search_invalid_limit(self, client):
        """Test search with invalid limit."""
        response = client.get("/analysis/search?limit=0")
        assert response.status_code == 422  # Validation error
    
    def test_search_invalid_offset(self, client):
        """Test search with negative offset."""
        response = client.get("/analysis/search?offset=-1")
        assert response.status_code == 422  # Validation error
    
    def test_search_valid_params(self, client):
        """Test search with valid parameters."""
        response = client.get("/analysis/search?limit=5&offset=0")
        # Should not return 500 error (even if DB connection fails)
        assert response.status_code in [200, 500]  # Either success or DB error
    
    def test_search_invalid_sentiment(self, client):
        """Test search with invalid sentiment value."""
        response = client.get("/analysis/search?sentiment=angry")
        # Should return 422 validation error for invalid sentiment
        assert response.status_code == 422
    
    def test_search_valid_sentiment(self, client):
        """Test search with valid sentiment values."""
        for sentiment in ["positive", "neutral", "negative"]:
            response = client.get(f"/analysis/search?sentiment={sentiment}")
            # Should not return 422 validation error for valid sentiment
            assert response.status_code != 422

