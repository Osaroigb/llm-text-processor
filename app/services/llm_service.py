import re
import json
import asyncio
import hashlib
from openai import AsyncOpenAI
from app.schemas import Metadata
from typing import Dict, Any, Optional, Union
from app.core.config import get_settings, setup_logging, get_logger

settings = get_settings()
setup_logging(settings)
logger = get_logger(__name__)

class LLMService:
    """Service wrapper for OpenAI LLM operations."""
    
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY

        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.model = settings.OPENAI_MODEL
    
    async def _chat_completion(self, **kwargs):
        """Wrapper for chat completion with retry logic."""
        # Simple retry logic - in production, consider using backoff library
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = await self.client.chat.completions.create(**kwargs)
                if response is None:
                    raise ValueError("Empty response from OpenAI API")
                return response
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                logger.warning(f"API call failed (attempt {attempt + 1}/{max_retries}): {e}")
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        # This should never be reached, but ensures type safety
        raise RuntimeError("Unexpected error in _chat_completion")
    
    async def generate_summary(self, text: str, max_sentences: int = 2, model: Optional[str] = None) -> str:
        """Generate a concise summary of the input text."""
        try:
            prompt = f"""Summarize the following text in exactly {max_sentences} sentences. Be concise and accurate.

Text: {text}

Summary:"""

            response = await self._chat_completion(
                model=model or self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that creates concise, accurate summaries. Respond only with the summary text."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.3
            )
            
            content = response.choices[0].message.content
            if content is None:
                raise ValueError("Empty response from OpenAI API")
            
            summary = content.strip()
            logger.info("Summary generated", extra={
                "event": "summary_generated",
                "summary_length": len(summary),
                "max_sentences": max_sentences
            })
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            raise
    
    async def extract_metadata(self, text: str, model: Optional[str] = None) -> Dict[str, Any]:
        """Extract structured metadata from text using LLM."""
        try:
            prompt = f"""Analyze the following text and extract metadata. Respond ONLY with a valid JSON object containing these exact fields:
- title: A descriptive, specific title that captures the main topic (max 50 chars, be specific and informative)
- topics: An array of exactly 3 key topics/themes (max 20 chars each)
- sentiment: One of: "positive", "neutral", or "negative"

Text: {text}

JSON:"""

            response = await self._chat_completion(
                model=model or self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that extracts structured metadata. Respond only with valid JSON. No markdown. No extra text."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.1
            )
            
            content = response.choices[0].message.content
            if content is None:
                raise ValueError("Empty response from OpenAI API")
            
            content = content.strip()
            
            # Extract JSON using regex for more robust parsing
            metadata = self._extract_json_from_response(content)
            
            # Use Pydantic for validation and normalization
            try:
                validated_metadata = Metadata(**metadata)
                logger.info("Metadata extracted and validated", extra={
                    "event": "metadata_extracted",
                    "title_length": len(validated_metadata.title),
                    "topics_count": len(validated_metadata.topics),
                    "sentiment": validated_metadata.sentiment
                })
                return validated_metadata.model_dump()
            except Exception as e:
                logger.warning(f"Metadata validation failed: {e}, using fallback")
                return self._get_fallback_metadata()
                
        except Exception as e:
            logger.error(f"Error extracting metadata: {e}")
            return self._get_fallback_metadata()
    
    def _extract_json_from_response(self, content: str) -> Dict[str, Any]:
        """Extract JSON from LLM response using regex."""
        # Try to find JSON block using regex
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        
        # Fallback: try to parse the entire content
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            raise ValueError("Invalid JSON response from LLM")
    

    
    def _get_fallback_metadata(self) -> Dict[str, Any]:
        """Return fallback metadata when LLM extraction fails."""
        return {
            "title": "Analysis Failed - Manual Review Required",
            "topics": ["general", "information", "content"],
            "sentiment": "neutral"
        }
    
    async def analyze_text(self, text: str, model: Optional[str] = None) -> Dict[str, Any]:
        """Complete text analysis combining summary and metadata extraction with true concurrency."""
        try:
            # Run both operations concurrently using asyncio.gather
            summary, metadata = await asyncio.gather(
                self.generate_summary(text, model=model),
                self.extract_metadata(text, model=model)
            )
            
            return {
                "summary": summary,
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"Error in complete text analysis: {e}")
            raise


# Mock LLM service for testing/development when API key is not available
class MockLLMService:
    """Mock LLM service for testing and development."""
    
    async def generate_summary(self, text: str, max_sentences: int = 2, model: Optional[str] = None) -> str:
        """Generate a mock summary."""
        words = text.split()[:20]  # Take first 20 words
        return f"This is a mock summary of the text containing: {' '.join(words)}..."
    
    async def extract_metadata(self, text: str, model: Optional[str] = None) -> Dict[str, Any]:
        """Generate mock metadata with input-dependent topics for more realistic testing."""
        # Generate deterministic topics based on input text hash
        text_hash = hashlib.md5(text.encode()).hexdigest()
        
        return {
            "title": f"Mock Title {text_hash[:6]}",
            "topics": [
                f"topic_{text_hash[:6]}",
                f"theme_{text_hash[6:12]}",
                f"subject_{text_hash[12:18]}"
            ],
            "sentiment": "neutral"
        }
    
    async def analyze_text(self, text: str, model: Optional[str] = None) -> Dict[str, Any]:
        """Complete mock text analysis."""
        return {
            "summary": await self.generate_summary(text, model=model),
            "metadata": await self.extract_metadata(text, model=model)
        }


def get_llm_service() -> Union[LLMService, MockLLMService]:
    """Factory function to get appropriate LLM service."""
    try:
        settings = get_settings()
        if not settings.OPENAI_API_KEY:
            logger.warning("OpenAI API key not available, using mock service")
            return MockLLMService()

        return LLMService()
    except ValueError:
        logger.warning("OpenAI API key not available, using mock service")
        return MockLLMService()
