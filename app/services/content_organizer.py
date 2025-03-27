from typing import Dict, List
from dataclasses import dataclass
import random
from app.services.nlp_processor import detect_topic

@dataclass
class Chapter:
    title: str
    content: List[str]
    key_points: List[str]
    quiz_questions: List[Dict]

@dataclass
class LearningCapsule:
    title: str
    description: str
    chapters: List[Chapter]
    estimated_duration: int  # in minutes
    difficulty: str  # beginner, intermediate, advanced
    tags: List[str]

class ContentOrganizer:
    def __init__(self):
        self.difficulty_levels = ['beginner', 'intermediate', 'advanced']
        
    def create_capsule(self, scraped_data: Dict) -> LearningCapsule:
        """Transform scraped content into a structured learning capsule"""
        main_topic = scraped_data.get('main_topic', 'Unknown Topic')
        
        # Create chapters from different content sources
        chapters = []
        for source in scraped_data.get('sources', []):
            if source['source'] == 'wikipedia':
                chapters.append(self._create_wikipedia_chapter(scraped_data))
            elif source['source'] == 'news':
                chapters.append(self._create_news_chapter(scraped_data))
            # Add more source types as needed
        
        # Ensure we have at least one chapter
        if not chapters:
            chapters.append(self._create_fallback_chapter(scraped_data))
        
        return LearningCapsule(
            title=f"Learning Capsule: {main_topic}",
            description=f"Comprehensive guide about {main_topic} compiled from multiple sources",
            chapters=chapters,
            estimated_duration=self._estimate_duration(chapters),
            difficulty=self._determine_difficulty(scraped_data),
            tags=scraped_data.get('related_topics', [])
        )
    
    def _create_wikipedia_chapter(self, data: Dict) -> Chapter:
        """Create a chapter from Wikipedia content"""
        wiki_content = next((s for s in data['sources'] if s['source'] == 'wikipedia'), None)
        content = wiki_content.get('content', []) if wiki_content else []
        
        return Chapter(
            title="Wikipedia Overview",
            content=content[:5],  # First 5 paragraphs
            key_points=data.get('key_points', [])[:3],
            quiz_questions=self._generate_quiz_questions(content, source="wikipedia")
        )
    
    def _create_news_chapter(self, data: Dict) -> Chapter:
        """Create a chapter from news articles"""
        news_content = next((s for s in data['sources'] if s['source'] == 'news'), None)
        articles = news_content.get('articles', []) if news_content else []
        
        return Chapter(
            title="Current Perspectives",
            content=[f"{a['title']} ({a['source']})" for a in articles],
            key_points=[a['title'] for a in articles[:3]],
            quiz_questions=self._generate_quiz_questions(articles, source="news")
        )
    
    def _create_fallback_chapter(self, data: Dict) -> Chapter:
        """Create a fallback chapter when no specific content is available"""
        return Chapter(
            title="Introduction",
            content=[f"Key information about {data.get('main_topic', 'this topic')}"],
            key_points=data.get('key_points', []),
            quiz_questions=[]
        )
    
    def _generate_quiz_questions(self, content: List, source: str) -> List[Dict]:
        """Generate simple quiz questions based on content"""
        questions = []
        
        if source == "wikipedia":
            # Generate questions from first few sentences
            for i, sentence in enumerate(content[:3]):
                if len(sentence.split()) > 8:  # Only use sufficiently long sentences
                    words = sentence.split()
                    blank = random.choice([w for w in words if len(w) > 4])
                    question = sentence.replace(blank, "_____")
                    questions.append({
                        'question': f"Fill in the blank: {question}",
                        'options': [blank, random.choice(words), "None of the above"],
                        'answer': blank
                    })
        
        elif source == "news":
            # Generate questions from article titles
            for i, article in enumerate(content[:3]):
                questions.append({
                    'question': f"What is the main subject of this news: '{article['title']}'?",
                    'options': [
                        article['title'].split()[0],  # First word
                        article['title'].split()[-1],  # Last word
                        "Current events",
                        "All of the above"
                    ],
                    'answer': "Current events"
                })
        
        return questions
    
    def _estimate_duration(self, chapters: List[Chapter]) -> int:
        """Estimate learning duration based on content length"""
        total_content = sum(len(chapter.content) for chapter in chapters)
        return min(120, max(15, total_content * 2))  # 2 minutes per content item
    
    def _determine_difficulty(self, data: Dict) -> str:
        """Determine difficulty level based on content analysis"""
        # Simple heuristic - more entities and longer content means more advanced
        entity_count = len(data.get('related_topics', []))
        if entity_count > 5:
            return 'advanced'
        elif entity_count > 2:
            return 'intermediate'
        return 'beginner'