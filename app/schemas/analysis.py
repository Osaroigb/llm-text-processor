from datetime import datetime
from typing import List, Dict, Any
from pydantic import BaseModel, Field

class AnalyzeRequest(BaseModel):
    """Request schema for text analysis."""
    text: str = Field(..., min_length=1, max_length=10000, description="Text to analyze")


class AnalysisResponse(BaseModel):
    """Response schema for text analysis."""
    id: int
    text: str
    summary: str
    metadata: Dict[str, Any]
    sentiment: str
    keywords: List[str]
    created_at: datetime


class SearchResponse(BaseModel):
    """Response schema for search results."""
    results: List[AnalysisResponse]
    total: int
    limit: int
    offset: int
