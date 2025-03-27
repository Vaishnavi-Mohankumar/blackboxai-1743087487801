import spacy
from typing import Dict, List

nlp = spacy.load("en_core_web_lg")

def detect_topic(text: str) -> Dict:
    """
    Analyze text to detect main topics and entities
    Returns dict with:
    - main_topic: primary subject
    - entities: list of relevant entities
    - categories: broad subject categories
    """
    doc = nlp(text)
    
    # Extract nouns and noun phrases as potential topics
    topics = [chunk.text for chunk in doc.noun_chunks]
    
    # Get named entities
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    
    return {
        "main_topic": topics[0] if topics else "General",
        "entities": entities,
        "categories": list(set([ent[1] for ent in entities]))
    }