import re
import nltk
from nltk.tag import pos_tag
from functools import lru_cache
from collections import Counter
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from typing import List, Tuple, Set, Dict, Union
from nltk.tokenize import word_tokenize, sent_tokenize

# Download required NLTK data once at module level
nltk.download('punkt', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)


@lru_cache(maxsize=1)
def _get_default_processor() -> 'NLPProcessor':
    """Get or create the default NLPProcessor instance using LRU cache."""
    return NLPProcessor()


class NLPProcessor:
    """NLP utilities for text processing and keyword extraction."""
    
    def __init__(self, stop_words: Set[str] | None = None, min_word_length: int = 2):
        # Normalize stopwords by lemmatizing them to match processed nouns
        raw_stop_words = stop_words or set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = {self.lemmatizer.lemmatize(w) for w in raw_stop_words}
        self.min_word_length = min_word_length
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        if not text or not text.strip():
            return ""
        
        # Convert to lowercase and remove special characters but keep spaces
        text = text.lower()
        text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
        # Remove extra whitespace
        return re.sub(r'\s+', ' ', text).strip()
    
    def extract_nouns(self, text: str) -> List[str]:
        """Extract nouns from text using POS tagging."""
        if not text or not text.strip():
            return []
        
        # Use clean_text for consistent tokenization across all methods
        tokens = word_tokenize(self.clean_text(text))
        pos_tags = pos_tag(tokens)
        
        return [
            self.lemmatizer.lemmatize(word)
            for word, tag in pos_tags
            if (tag.startswith('NN') and 
                len(word) > self.min_word_length and 
                word not in self.stop_words)
        ]
    
    def get_keyword_frequency(self, text: str, top_n: int = 3) -> List[Tuple[str, int]]:
        """Get the most frequent nouns as keywords."""
        nouns = self.extract_nouns(text)
        return Counter(nouns).most_common(top_n) if nouns else []
    
    def extract_keywords(self, text: str, top_n: int = 3) -> List[str]:
        """Extract top N keywords from text."""
        return [keyword for keyword, _ in self.get_keyword_frequency(text, top_n)]
    
    def get_sentence_count(self, text: str) -> int:
        """Get the number of sentences in the text."""
        if not text or not text.strip():
            return 0
        return len(sent_tokenize(text))
    
    def get_word_count(self, text: str) -> int:
        """Get the number of words in the text."""
        if not text or not text.strip():
            return 0
        
        # Use clean_text for consistent tokenization
        words = word_tokenize(self.clean_text(text))
        return len([word for word in words if word not in self.stop_words])


# Convenience functions using the cached default processor
def extract_keywords(text: str, top_n: int = 3) -> List[str]:
    """Extract top N keywords from text using default NLP processor."""
    return _get_default_processor().extract_keywords(text, top_n)


def get_text_stats(text: str, top_n: int = 3) -> Dict[str, Union[int, List[str], List[Tuple[str, int]]]]:
    """Get comprehensive text statistics including keyword frequencies."""
    if not text or not text.strip():
        return {
            'word_count': 0,
            'sentence_count': 0,
            'keywords': [],
            'keyword_frequency': []
        }
    
    processor = _get_default_processor()
    return {
        'word_count': processor.get_word_count(text),
        'sentence_count': processor.get_sentence_count(text),
        'keywords': processor.extract_keywords(text, top_n),
        'keyword_frequency': processor.get_keyword_frequency(text, top_n)
    }


def create_processor(stop_words: Set[str] | None = None, min_word_length: int = 2) -> NLPProcessor:
    """Create a custom NLPProcessor instance with specific configuration."""
    return NLPProcessor(stop_words=stop_words, min_word_length=min_word_length)
