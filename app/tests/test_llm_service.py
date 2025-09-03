import json
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.llm_service import (
    LLMService, 
    MockLLMService, 
    get_llm_service
)


class TestMockLLMService:
    """Test cases for MockLLMService."""
    
    @pytest.fixture
    def mock_service(self):
        """Create a fresh MockLLMService instance for each test."""
        return MockLLMService()
    
    @pytest.mark.asyncio
    async def test_generate_summary(self, mock_service):
        """Test mock summary generation."""
        text = "This is a test text for summary generation."
        summary = await mock_service.generate_summary(text)
        
        assert isinstance(summary, str)
        assert len(summary) > 0
        assert "test" in summary.lower()
    
    @pytest.mark.asyncio
    async def test_extract_metadata(self, mock_service):
        """Test mock metadata extraction."""
        text = "Sample text for metadata extraction."
        metadata = await mock_service.extract_metadata(text)
        
        assert isinstance(metadata, dict)
        assert "title" in metadata
        assert "topics" in metadata
        assert "sentiment" in metadata
        
        # Mock service now generates dynamic titles based on text hash
        assert metadata["title"].startswith("Mock Title")
        assert isinstance(metadata["topics"], list)
        assert len(metadata["topics"]) == 3
        assert metadata["sentiment"] == "neutral"
    
    @pytest.mark.asyncio
    async def test_analyze_text(self, mock_service):
        """Test complete mock text analysis."""
        text = "Complete text analysis test."
        result = await mock_service.analyze_text(text)
        
        assert isinstance(result, dict)
        assert "summary" in result
        assert "metadata" in result
        
        assert isinstance(result["summary"], str)
        assert isinstance(result["metadata"], dict)


class TestLLMService:
    """Test cases for LLMService."""
    
    @pytest.fixture
    def mock_openai_client(self):
        """Create a mock OpenAI client."""
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test response"
        mock_client.chat.completions.create.return_value = mock_response
        return mock_client
    
    @pytest.fixture
    def llm_service(self, mock_openai_client):
        """Create LLMService with mocked OpenAI client."""
        with patch('app.services.llm_service.AsyncOpenAI') as mock_openai:
            mock_openai.return_value = mock_openai_client
            with patch('app.services.llm_service.settings') as mock_settings:
                mock_settings.OPENAI_API_KEY = "test_key"
                mock_settings.OPENAI_MODEL = "gpt-3.5-turbo"
                service = LLMService()
                return service
    
    @pytest.mark.asyncio
    async def test_init_with_api_key(self):
        """Test LLMService initialization with API key."""
        with patch('app.services.llm_service.AsyncOpenAI') as mock_openai:
            mock_openai.return_value = AsyncMock()
            with patch('app.services.llm_service.settings') as mock_settings:
                mock_settings.OPENAI_API_KEY = "test_key"
                mock_settings.OPENAI_MODEL = "gpt-3.5-turbo"
                service = LLMService()
                
                assert service.api_key == "test_key"
                assert service.model == "gpt-3.5-turbo"
    
    def test_init_without_api_key_raises_error(self):
        """Test that LLMService raises error without API key."""
        with patch('app.services.llm_service.settings') as mock_settings:
            mock_settings.OPENAI_API_KEY = None
            with pytest.raises(ValueError, match="OpenAI API key is required"):
                LLMService()
    
    @pytest.mark.asyncio
    async def test_generate_summary(self, llm_service, mock_openai_client):
        """Test summary generation."""
        mock_openai_client.chat.completions.create.return_value.choices[0].message.content = "This is a test summary."
        
        text = "Sample text for summary generation."
        summary = await llm_service.generate_summary(text)
        
        assert summary == "This is a test summary."
        mock_openai_client.chat.completions.create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_extract_metadata_success(self, llm_service, mock_openai_client):
        """Test successful metadata extraction."""
        mock_response = {
            "title": "Test Title",
            "topics": ["topic1", "topic2", "topic3"],
            "sentiment": "positive"
        }
        mock_openai_client.chat.completions.create.return_value.choices[0].message.content = json.dumps(mock_response)
        
        text = "Sample text for metadata extraction."
        metadata = await llm_service.extract_metadata(text)
        
        assert metadata["title"] == "Test Title"
        assert metadata["topics"] == ["topic1", "topic2", "topic3"]
        assert metadata["sentiment"] == "positive"
    
    @pytest.mark.asyncio
    async def test_extract_metadata_with_markdown(self, llm_service, mock_openai_client):
        """Test metadata extraction with markdown formatting."""
        mock_response = {
            "title": "Test Title",
            "topics": ["topic1", "topic2", "topic3"],
            "sentiment": "neutral"
        }
        markdown_response = f"```json\n{json.dumps(mock_response)}\n```"
        mock_openai_client.chat.completions.create.return_value.choices[0].message.content = markdown_response
        
        text = "Sample text for metadata extraction."
        metadata = await llm_service.extract_metadata(text)
        
        assert metadata["title"] == "Test Title"
        assert metadata["topics"] == ["topic1", "topic2", "topic3"]
        assert metadata["sentiment"] == "neutral"
    
    @pytest.mark.asyncio
    async def test_extract_metadata_invalid_json_fallback(self, llm_service, mock_openai_client):
        """Test metadata extraction fallback with invalid JSON."""
        mock_openai_client.chat.completions.create.return_value.choices[0].message.content = "Invalid JSON response"
        
        text = "Sample text for metadata extraction."
        metadata = await llm_service.extract_metadata(text)
        
        # Should return fallback metadata
        assert metadata["title"] == "Analysis Failed - Manual Review Required"
        assert metadata["topics"] == ["general", "information", "content"]
        assert metadata["sentiment"] == "neutral"
    
    @pytest.mark.asyncio
    async def test_extract_metadata_missing_fields_fallback(self, llm_service, mock_openai_client):
        """Test metadata extraction with missing fields - Pydantic provides defaults."""
        mock_response = {
            "title": "Test Title"
            # Missing topics and sentiment
        }
        mock_openai_client.chat.completions.create.return_value.choices[0].message.content = json.dumps(mock_response)
        
        text = "Sample text for metadata extraction."
        metadata = await llm_service.extract_metadata(text)
        
        # Pydantic automatically provides defaults for missing fields
        assert metadata["title"] == "Test Title"  # Title is provided
        assert metadata["topics"] == ["general", "information", "content"]  # Default topics
        assert metadata["sentiment"] == "neutral"  # Default sentiment
    
    @pytest.mark.asyncio
    async def test_extract_metadata_invalid_sentiment_fallback(self, llm_service, mock_openai_client):
        """Test metadata extraction with invalid sentiment value."""
        mock_response = {
            "title": "Test Title",
            "topics": ["topic1", "topic2", "topic3"],
            "sentiment": "invalid_sentiment"
        }
        mock_openai_client.chat.completions.create.return_value.choices[0].message.content = json.dumps(mock_response)
        
        text = "Sample text for metadata extraction."
        metadata = await llm_service.extract_metadata(text)
        
        # Should normalize invalid sentiment to neutral
        assert metadata["sentiment"] == "neutral"
    
    @pytest.mark.asyncio
    async def test_extract_metadata_topics_not_list(self, llm_service, mock_openai_client):
        """Test metadata extraction with topics not as a list."""
        mock_response = {
            "title": "Test Title",
            "topics": "single_topic",  # Not a list
            "sentiment": "positive"
        }
        mock_openai_client.chat.completions.create.return_value.choices[0].message.content = json.dumps(mock_response)
        
        text = "Sample text for metadata extraction."
        metadata = await llm_service.extract_metadata(text)
        
        # Should convert to list and pad to 3 items
        assert isinstance(metadata["topics"], list)
        assert len(metadata["topics"]) == 3
        assert metadata["topics"][0] == "single_topic"
    
    @pytest.mark.asyncio
    async def test_extract_metadata_topics_padding(self, llm_service, mock_openai_client):
        """Test metadata extraction with topics padding."""
        mock_response = {
            "title": "Test Title",
            "topics": ["topic1"],  # Only 1 topic
            "sentiment": "positive"
        }
        mock_openai_client.chat.completions.create.return_value.choices[0].message.content = json.dumps(mock_response)
        
        text = "Sample text for metadata extraction."
        metadata = await llm_service.extract_metadata(text)
        
        # Should pad to 3 topics
        assert len(metadata["topics"]) == 3
        assert metadata["topics"][0] == "topic1"
        assert metadata["topics"][1] == "information"  # Updated padding logic
        assert metadata["topics"][2] == "content"
    
    @pytest.mark.asyncio
    async def test_extract_metadata_topics_truncation(self, llm_service, mock_openai_client):
        """Test metadata extraction with topics truncation."""
        mock_response = {
            "title": "Test Title",
            "topics": ["topic1", "topic2", "topic3", "topic4", "topic5"],  # 5 topics
            "sentiment": "positive"
        }
        mock_openai_client.chat.completions.create.return_value.choices[0].message.content = json.dumps(mock_response)
        
        text = "Sample text for metadata extraction."
        metadata = await llm_service.extract_metadata(text)
        
        # Should truncate to 3 topics
        assert len(metadata["topics"]) == 3
        assert metadata["topics"] == ["topic1", "topic2", "topic3"]
    
    @pytest.mark.asyncio
    async def test_analyze_text(self, llm_service, mock_openai_client):
        """Test complete text analysis."""
        # Mock summary response
        summary_response = MagicMock()
        summary_response.choices[0].message.content = "Test summary"
        
        # Mock metadata response
        metadata_response = MagicMock()
        metadata_response.choices[0].message.content = json.dumps({
            "title": "Test Title",
            "topics": ["topic1", "topic2", "topic3"],
            "sentiment": "positive"
        })
        
        # Configure mock to return different responses for different calls
        mock_openai_client.chat.completions.create.side_effect = [summary_response, metadata_response]
        
        text = "Sample text for analysis."
        result = await llm_service.analyze_text(text)
        
        assert "summary" in result
        assert "metadata" in result
        assert result["summary"] == "Test summary"
        assert result["metadata"]["title"] == "Test Title"
    
    @pytest.mark.asyncio
    async def test_generate_summary_error_handling(self, llm_service, mock_openai_client):
        """Test error handling in summary generation."""
        mock_openai_client.chat.completions.create.side_effect = Exception("API Error")
        
        text = "Sample text for summary generation."
        
        with pytest.raises(Exception, match="API Error"):
            await llm_service.generate_summary(text)
    
    @pytest.mark.asyncio
    async def test_extract_metadata_error_handling(self, llm_service, mock_openai_client):
        """Test error handling in metadata extraction."""
        mock_openai_client.chat.completions.create.side_effect = Exception("API Error")
        
        text = "Sample text for metadata extraction."
        metadata = await llm_service.extract_metadata(text)
        
        # Should return fallback metadata on error
        assert metadata["title"] == "Analysis Failed - Manual Review Required"
        assert metadata["topics"] == ["general", "information", "content"]
        assert metadata["sentiment"] == "neutral"


class TestGetLLMService:
    """Test cases for get_llm_service factory function."""
    
    @pytest.mark.asyncio
    async def test_get_llm_service_with_api_key(self):
        """Test getting LLM service when API key is available."""
        with patch('app.services.llm_service.get_settings') as mock_settings:
            mock_settings.return_value.OPENAI_API_KEY = "test_key"
            with patch('app.services.llm_service.LLMService') as mock_llm_service:
                mock_llm_service.return_value = MagicMock()
                
                service = get_llm_service()
                
                assert service is not None
                mock_llm_service.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_llm_service_without_api_key_fallback(self):
        """Test getting LLM service fallback when API key is not available."""
        with patch('app.services.llm_service.get_settings') as mock_settings:
            mock_settings.return_value.OPENAI_API_KEY = None
            with patch('app.services.llm_service.MockLLMService') as mock_mock_service:
                mock_mock_service.return_value = MagicMock()
                
                service = get_llm_service()
                
                assert service is not None
                mock_mock_service.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_llm_service_value_error_fallback(self):
        """Test getting LLM service fallback when LLMService raises ValueError."""
        with patch('app.services.llm_service.get_settings') as mock_settings:
            mock_settings.return_value.OPENAI_API_KEY = "test_key"
            with patch('app.services.llm_service.LLMService') as mock_llm_service:
                mock_llm_service.side_effect = ValueError("API key error")
                with patch('app.services.llm_service.MockLLMService') as mock_mock_service:
                    mock_mock_service.return_value = MagicMock()
                    
                    service = get_llm_service()
                    
                    assert service is not None
                    mock_mock_service.assert_called_once()


class TestIntegration:
    """Integration tests for LLM service."""
    
    @pytest.mark.asyncio
    async def test_mock_service_integration(self):
        """Test that mock service provides consistent results."""
        service = MockLLMService()
        
        text = "Integration test text for LLM service."
        
        # Test all methods work together
        summary = await service.generate_summary(text)
        metadata = await service.extract_metadata(text)
        analysis = await service.analyze_text(text)
        
        assert isinstance(summary, str)
        assert isinstance(metadata, dict)
        assert isinstance(analysis, dict)
        
        # Analysis should contain both summary and metadata
        assert analysis["summary"] == summary
        assert analysis["metadata"] == metadata
    
    @pytest.mark.asyncio
    async def test_service_consistency(self):
        """Test that service provides consistent results across calls."""
        service = MockLLMService()
        
        text = "Consistency test text."
        
        # Call multiple times
        result1 = await service.analyze_text(text)
        result2 = await service.analyze_text(text)
        
        # Results should be consistent
        assert result1 == result2
