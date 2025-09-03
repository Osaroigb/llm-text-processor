from app.core.db import Base
from typing import Dict, Any
from sqlalchemy.sql import func
from sqlalchemy import Column, Integer, Text, DateTime, JSON, String


class Analysis(Base):
    """Analysis model for storing LLM text processing results."""
    
    __tablename__ = "analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False, comment="Original input text")
    summary = Column(Text, nullable=True, comment="LLM-generated summary")
    analysis_metadata = Column(JSON, nullable=True, comment="Additional analysis metadata")
    sentiment = Column(String(50), nullable=True, comment="Sentiment analysis result")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="Creation timestamp")
    
    def __repr__(self):
        return f"<Analysis(id={self.id}, sentiment={self.sentiment})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        created_at_str = None
        if hasattr(self, 'created_at') and self.created_at is not None:
            created_at_str = self.created_at.isoformat()
            
        return {
            "id": self.id,
            "text": self.text,
            "summary": self.summary,
            "metadata": self.analysis_metadata,  # Keep 'metadata' in the API response
            "sentiment": self.sentiment,
            "created_at": created_at_str
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Analysis":
        """Create model instance from dictionary."""
        return cls(
            text=data.get("text"),
            summary=data.get("summary"),
            analysis_metadata=data.get("metadata"),  # Map 'metadata' from API to 'analysis_metadata' in DB
            sentiment=data.get("sentiment")
        )
