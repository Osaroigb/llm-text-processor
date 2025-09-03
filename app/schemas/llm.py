from pydantic import BaseModel, Field, field_validator


class Metadata(BaseModel):
    """Pydantic model for LLM metadata validation."""
    title: str = Field(default="No Title Generated", max_length=50)
    topics: list[str] = Field(default_factory=lambda: ["general", "information", "content"])
    sentiment: str = Field(default="neutral")

    @field_validator("sentiment", mode="before")
    @classmethod
    def normalize_sentiment(cls, v):
        """Normalize sentiment to valid values."""
        return v if v in ["positive", "neutral", "negative"] else "neutral"

    @field_validator("topics", mode="before")
    @classmethod
    def ensure_topics(cls, v):
        """Ensure exactly 3 topics with proper padding."""
        if not isinstance(v, list):
            v = [v] if v else []
        
        # Pad with meaningful defaults if less than 3
        while len(v) < 3:
            if len(v) == 0:
                v.append("general")
            elif len(v) == 1:
                v.append("information")
            else:
                v.append("content")
        
        return v[:3]  # Truncate if more than 3
