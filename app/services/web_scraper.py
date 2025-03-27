import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import re
from urllib.parse import urlparse
from app.services.nlp_processor import detect_topic

class WebScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.content_sources = {
            'wikipedia': self._scrape_wikipedia,
            'news': self._scrape_news,
            'educational': self._scrape_educational
        }

    def scrape_content(self, topic: str, sources: Optional[List[str]] = None) -> Dict:
        """
        Main method to scrape content from various sources based on topic
        """
        sources = sources or list(self.content_sources.keys())
        results = {}
        
        for source in sources:
            if source in self.content_sources:
                try:
                    results[source] = self.content_sources[source](topic)
                except Exception as e:
                    print(f"Error scraping {source}: {str(e)}")
                    continue
        
        return self._process_results(results)

    def _scrape_wikipedia(self, topic: str) -> Dict:
        """Scrape content from Wikipedia"""
        url = f"https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}"
        response = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract main content
        content_div = soup.find('div', {'id': 'mw-content-text'})
        paragraphs = [p.get_text().strip() for p in content_div.find_all('p') if p.get_text().strip()]
        
        return {
            'source': 'wikipedia',
            'url': url,
            'content': paragraphs[:10],  # First 10 paragraphs
            'tables': [str(table) for table in content_div.find_all('table', {'class': 'wikitable'})[:2]]
        }

    def _scrape_news(self, topic: str) -> Dict:
        """Scrape recent news articles about the topic"""
        # Using NewsAPI would be better here, but for demo using Google News
        url = f"https://news.google.com/search?q={topic.replace(' ', '+')}"
        response = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        articles = []
        for article in soup.find_all('article')[:5]:  # First 5 articles
            title = article.find('h3').get_text()
            source = article.find('div', {'class': 'vr1PYe'}).get_text()
            time = article.find('time')['datetime']
            articles.append({
                'title': title,
                'source': source,
                'time': time
            })
            
        return {
            'source': 'news',
            'url': url,
            'articles': articles
        }

    def _scrape_educational(self, topic: str) -> Dict:
        """Scrape educational content from various sources"""
        # Placeholder - would integrate with Khan Academy, Coursera, etc.
        return {
            'source': 'educational',
            'content': f"Educational resources about {topic} would be fetched here"
        }

    def _process_results(self, raw_results: Dict) -> Dict:
        """Process and clean scraped content"""
        processed = {
            'main_topic': None,
            'sources': [],
            'key_points': [],
            'related_topics': set()
        }
        
        for source, data in raw_results.items():
            processed['sources'].append({
                'source': source,
                'url': data.get('url'),
                'content_type': list(data.keys())
            })
            
            # Extract key points from content
            if 'content' in data:
                content_text = ' '.join(data['content'])
                topic_info = detect_topic(content_text)
                if not processed['main_topic']:
                    processed['main_topic'] = topic_info['main_topic']
                
                processed['related_topics'].update([e[0] for e in topic_info['entities']])
                
                # Simple extraction of key sentences
                sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', content_text)
                processed['key_points'].extend(sentences[:5])  # First 5 sentences as key points
        
        processed['related_topics'] = list(processed['related_topics'])
        return processed