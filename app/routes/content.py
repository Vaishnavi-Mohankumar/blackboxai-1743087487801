from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.services.web_scraper import WebScraper
from app.services.content_organizer import ContentOrganizer
import logging

router = APIRouter(prefix="/content", tags=["content"])

class ContentRequest(BaseModel):
    topic: str
    sources: Optional[List[str]] = None

class ContentResponse(BaseModel):
    title: str
    description: str
    chapters: List[dict]
    estimated_duration: int
    difficulty: str
    tags: List[str]

@router.post("/generate", response_model=ContentResponse)
async def generate_content(request: ContentRequest):
    try:
        # Scrape content from various sources
        scraper = WebScraper()
        scraped_data = scraper.scrape_content(request.topic, request.sources)
        
        # Organize into learning capsule
        organizer = ContentOrganizer()
        capsule = organizer.create_capsule(scraped_data)
        
        # Convert dataclass to dict for response
        return {
            "title": capsule.title,
            "description": capsule.description,
            "chapters": [
                {
                    "title": chapter.title,
                    "content": chapter.content,
                    "key_points": chapter.key_points,
                    "quiz_questions": chapter.quiz_questions
                }
                for chapter in capsule.chapters
            ],
            "estimated_duration": capsule.estimated_duration,
            "difficulty": capsule.difficulty,
            "tags": capsule.tags
        }
        
    except Exception as e:
        logging.error(f"Error generating content: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate content: {str(e)}"
        )