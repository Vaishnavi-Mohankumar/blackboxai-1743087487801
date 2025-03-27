import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.routes.content import ContentRequest
from app.services.web_scraper import WebScraper
from app.services.content_organizer import ContentOrganizer

client = TestClient(app)

def test_web_scraper():
    """Test the web scraper service"""
    scraper = WebScraper()
    result = scraper.scrape_content("Artificial Intelligence", ["wikipedia"])
    
    assert isinstance(result, dict)
    assert "main_topic" in result
    assert "sources" in result
    assert len(result["sources"]) > 0

def test_content_organizer():
    """Test the content organizer service"""
    scraper = WebScraper()
    scraped_data = scraper.scrape_content("Machine Learning", ["wikipedia"])
    
    organizer = ContentOrganizer()
    capsule = organizer.create_capsule(scraped_data)
    
    assert capsule.title.startswith("Learning Capsule")
    assert len(capsule.chapters) > 0
    assert capsule.estimated_duration > 0
    assert capsule.difficulty in ["beginner", "intermediate", "advanced"]

def test_content_generation_endpoint():
    """Test the content generation API endpoint"""
    test_data = {
        "topic": "Neural Networks",
        "sources": ["wikipedia"]
    }
    
    response = client.post(
        "/content/generate",
        json=test_data
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "title" in data
    assert "chapters" in data
    assert len(data["chapters"]) > 0

def test_error_handling():
    """Test error handling for invalid requests"""
    response = client.post(
        "/content/generate",
        json={"invalid": "request"}
    )
    assert response.status_code == 422  # Validation error

    # Test with non-existent source
    response = client.post(
        "/content/generate",
        json={"topic": "test", "sources": ["invalid_source"]}
    )
    assert response.status_code == 200  # Should handle gracefully