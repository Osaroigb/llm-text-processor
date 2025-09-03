from app.core.db import Base
from typing import Dict, Any
from sqlalchemy.sql import func
from sqlalchemy import Column, Integer, Text, DateTime, JSON, String, Enum
import enum


class SentimentEnum(str, enum.Enum):
    """Enum for sentiment values to ensure type safety across DB, ORM, and API."""
    positive = "positive"
    neutral = "neutral"
    negative = "negative"


class Analysis(Base):
    """Analysis model for storing LLM text processing results."""
    
    __tablename__ = "analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False, comment="Original input text")
    summary = Column(Text, nullable=True, comment="LLM-generated summary")
    analysis_metadata = Column(JSON, nullable=True, comment="Additional analysis metadata")
    sentiment = Column(Enum(SentimentEnum), nullable=True, comment="Sentiment analysis result")
    keywords = Column(JSON, nullable=True, comment="Extracted keywords from text")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="Creation timestamp")
    
    def __repr__(self):
        return f"<Analysis(id={self.id}, sentiment={self.sentiment})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "text": self.text,
            "summary": self.summary,
            "metadata": self.analysis_metadata,  # Keep 'metadata' in the API response
            "sentiment": self.sentiment,
            "keywords": self.keywords or [],
            "created_at": self.created_at  # Return datetime directly
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Analysis":
        """Create model instance from dictionary."""
        return cls(
            text=data.get("text"),
            summary=data.get("summary"),
            analysis_metadata=data.get("metadata"),  # Map 'metadata' from API to 'analysis_metadata' in DB
            sentiment=data.get("sentiment"),
            keywords=data.get("keywords")
        )
