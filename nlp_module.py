import spacy
from textblob import TextBlob

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

def analyze_text_local(text):
    """Analyze sentiment and extract keywords without API calls."""
    doc = nlp(text)
    keywords = [token.text for token in doc if token.is_alpha and not token.is_stop]
    blob = TextBlob(text)
    sentiment = blob.sentiment.polarity
    return {
        "keywords": list(set(keywords)),
        "sentiment": "positive" if sentiment > 0 else "negative" if sentiment < 0 else "neutral"
    }

def classify_needs_wants(category):
    """Classify an expense as Need or Want."""
    needs = ["food", "rent", "utilities", "transport", "health", "medicine", "electricity", "water"]
    return "Need" if category.lower() in needs else "Want"
