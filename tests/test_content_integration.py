import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.web_scraper import WebScraper
from app.services.content_organizer import ContentOrganizer

@pytest.fixture
def client():
    return TestClient(app)

def test_web_scraper_integration():
    """Test web scraper integration"""
    scraper = WebScraper()
    result = scraper.scrape_content("Python Programming", ["wikipedia"])
    assert isinstance(result, dict)
    assert "main_topic" in result

def test_content_endpoint(client):
    """Test content generation endpoint"""
    response = client.post(
        "/content/generate",
        json={"topic": "Data Science", "sources": ["wikipedia"]}
    )
    assert response.status_code == 200
    data = response.json()
    assert "title" in data
    assert "chapters" in data