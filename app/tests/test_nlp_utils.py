import pytest
from app.services.nlp_utils import (
    NLPProcessor, 
    extract_keywords, 
    get_text_stats,
    NLPProcessor
)


class TestNLPProcessor:
    """Test cases for NLPProcessor class."""
    
    @pytest.fixture
    def processor(self):
        """Create a fresh NLPProcessor instance for each test."""
        return NLPProcessor()
    
    @pytest.fixture
    def sample_text(self):
        """Sample text for testing."""
        return """
        Artificial Intelligence is transforming the technology industry. 
        Machine learning algorithms are becoming more sophisticated every day. 
        Companies are investing heavily in AI research and development.
        """
    
    def test_clean_text(self, processor):
        """Test text cleaning functionality."""
        dirty_text = "  Hello, World!   This is a TEST.  "
        cleaned = processor.clean_text(dirty_text)
        assert cleaned == "hello world this is a test"
        
        # Test with special characters
        special_text = "Text with @#$%^&*() symbols!"
        cleaned = processor.clean_text(special_text)
        assert cleaned == "text with symbols"
    
    def test_extract_nouns(self, processor, sample_text):
        """Test noun extraction from text."""
        nouns = processor.extract_nouns(sample_text)
        
        # Should extract nouns like "intelligence", "technology", "algorithms", etc.
        assert len(nouns) > 0
        assert all(isinstance(noun, str) for noun in nouns)
        
        # Test with simple text
        simple_text = "The cat sat on the mat."
        nouns = processor.extract_nouns(simple_text)
        assert "cat" in nouns or "mat" in nouns
    
    def test_get_keyword_frequency(self, processor, sample_text):
        """Test keyword frequency extraction."""
        keyword_freq = processor.get_keyword_frequency(sample_text, top_n=3)
        
        assert len(keyword_freq) <= 3
        assert all(isinstance(item, tuple) for item in keyword_freq)
        assert all(len(item) == 2 for item in keyword_freq)
        assert all(isinstance(item[0], str) and isinstance(item[1], int) for item in keyword_freq)
        
        # Test with empty text
        empty_freq = processor.get_keyword_frequency("", top_n=3)
        assert empty_freq == []
    
    def test_extract_keywords(self, processor, sample_text):
        """Test keyword extraction."""
        keywords = processor.extract_keywords(sample_text, top_n=3)
        
        assert len(keywords) <= 3
        assert all(isinstance(keyword, str) for keyword in keywords)
        
        # Test with different top_n values
        keywords_5 = processor.extract_keywords(sample_text, top_n=5)
        assert len(keywords_5) <= 5
    
    def test_get_sentence_count(self, processor, sample_text):
        """Test sentence counting."""
        sentence_count = processor.get_sentence_count(sample_text)
        assert sentence_count > 0
        assert isinstance(sentence_count, int)
        
        # Test with single sentence
        single_sentence = "This is one sentence."
        assert processor.get_sentence_count(single_sentence) == 1
        
        # Test with empty text
        assert processor.get_sentence_count("") == 0
    
    def test_get_word_count(self, processor, sample_text):
        """Test word counting."""
        word_count = processor.get_word_count(sample_text)
        assert word_count > 0
        assert isinstance(word_count, int)
        
        # Test with simple text
        simple_text = "one two three four"
        assert processor.get_word_count(simple_text) == 4
        
        # Test with empty text
        assert processor.get_word_count("") == 0
    
    def test_filter_short_words(self, processor):
        """Test that very short words are filtered out."""
        short_text = "A I am the cat sat on a mat."
        nouns = processor.extract_nouns(short_text)
        
        # Should not contain single letters or very short words
        assert not any(len(noun) <= 2 for noun in nouns)
    
    def test_stop_words_filtering(self, processor):
        """Test that stop words are filtered out."""
        text_with_stops = "The quick brown fox jumps over the lazy dog."
        nouns = processor.extract_nouns(text_with_stops)
        
        # Should not contain common stop words
        stop_words = {"the", "quick", "over", "lazy"}
        for stop_word in stop_words:
            assert stop_word not in nouns


class TestConvenienceFunctions:
    """Test cases for convenience functions."""
    
    def test_extract_keywords_function(self):
        """Test the extract_keywords convenience function."""
        text = "Machine learning and artificial intelligence are transforming technology."
        keywords = extract_keywords(text, top_n=3)
        
        assert len(keywords) <= 3
        assert all(isinstance(keyword, str) for keyword in keywords)
    
    def test_get_text_stats(self):
        """Test the get_text_stats convenience function."""
        text = "This is a test sentence. It has multiple sentences for testing."
        stats = get_text_stats(text)
        
        assert "word_count" in stats
        assert "sentence_count" in stats
        assert "keywords" in stats
        
        assert isinstance(stats["word_count"], int)
        assert isinstance(stats["sentence_count"], int)
        assert isinstance(stats["keywords"], list)
        assert len(stats["keywords"]) <= 3


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    @pytest.fixture
    def processor(self):
        return NLPProcessor()
    
    def test_empty_text(self, processor):
        """Test behavior with empty text."""
        assert processor.clean_text("") == ""
        assert processor.extract_nouns("") == []
        assert processor.get_keyword_frequency("", 3) == []
        assert processor.extract_keywords("", 3) == []
        assert processor.get_sentence_count("") == 0
        assert processor.get_word_count("") == 0
    
    def test_whitespace_only_text(self, processor):
        """Test behavior with whitespace-only text."""
        whitespace_text = "   \n\t   "
        assert processor.clean_text(whitespace_text) == ""
        assert processor.extract_nouns(whitespace_text) == []
    
    def test_single_word_text(self, processor):
        """Test behavior with single word text."""
        single_word = "Hello"
        assert processor.clean_text(single_word) == "hello"
        
        # Single word might not have nouns depending on POS tagging
        nouns = processor.extract_nouns(single_word)
        # Just ensure it returns a list
        assert isinstance(nouns, list)
    
    def test_numbers_and_symbols(self, processor):
        """Test behavior with numbers and symbols."""
        mixed_text = "Text with 123 numbers and @#$ symbols!"
        cleaned = processor.clean_text(mixed_text)
        assert "123" in cleaned
        assert "@#$" not in cleaned
    
    def test_very_long_text(self, processor):
        """Test behavior with very long text."""
        long_text = "word " * 1000  # 1000 words
        word_count = processor.get_word_count(long_text)
        assert word_count > 0
        assert word_count <= 1000  # Should be less due to stop word filtering


class TestIntegration:
    """Integration tests for the complete NLP pipeline."""
    
    @pytest.fixture
    def processor(self):
        return NLPProcessor()
    
    def test_complete_pipeline(self, processor):
        """Test the complete NLP processing pipeline."""
        text = """
        Artificial Intelligence and Machine Learning are revolutionizing the technology sector.
        Companies worldwide are investing billions in AI research and development.
        The future of work will be shaped by these emerging technologies.
        """
        
        # Test each step
        cleaned = processor.clean_text(text)
        assert len(cleaned) > 0
        
        nouns = processor.extract_nouns(cleaned)
        assert len(nouns) > 0
        
        keywords = processor.extract_keywords(cleaned, 3)
        assert len(keywords) <= 3
        
        sentence_count = processor.get_sentence_count(text)
        assert sentence_count == 3
        
        word_count = processor.get_word_count(cleaned)
        assert word_count > 0
    
    def test_keyword_consistency(self, processor):
        """Test that keywords are consistent across multiple calls."""
        text = "Machine learning algorithms process data efficiently."
        
        keywords1 = processor.extract_keywords(text, 3)
        keywords2 = processor.extract_keywords(text, 3)
        
        # Keywords should be the same for the same text
        assert keywords1 == keywords2
