from app.models.analysis import Analysis, SentimentEnum
from sqlalchemy import select, or_, func
from app.core.db import get_async_db as get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.nlp_utils import extract_keywords
from app.services.llm_service import get_llm_service
from app.core.config import get_settings, setup_logging, get_logger
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Literal

from app.schemas.analysis import (
    AnalyzeRequest, 
    AnalysisResponse, 
    SearchResponse
)

settings = get_settings()
setup_logging(settings)
logger = get_logger(__name__)

router = APIRouter(prefix="/analysis", tags=["analysis"])

@router.post("/analyze", response_model=AnalysisResponse, status_code=status.HTTP_201_CREATED)
async def analyze_text(
    request: AnalyzeRequest,
    db: AsyncSession = Depends(get_db)
):
    """Analyze text using LLM and NLP services."""
    try:
        # Get LLM service
        llm_service = get_llm_service()
        
        # Perform text analysis
        analysis_result = await llm_service.analyze_text(request.text)
        
        # Extract keywords using NLP utils
        keywords = extract_keywords(request.text, top_n=5)
        
        # Create analysis record
        analysis = Analysis(
            text=request.text,
            summary=analysis_result["summary"],
            analysis_metadata=analysis_result["metadata"],
            sentiment=analysis_result["metadata"]["sentiment"],
            keywords=keywords
        )
        
        # Save to database
        db.add(analysis)
        await db.commit()
        await db.refresh(analysis)
        
        # Convert model to dict (metadata already mapped in to_dict())
        analysis_dict = analysis.to_dict()
        analysis_dict["keywords"] = keywords
        
        # Return response
        return AnalysisResponse(**analysis_dict)
        
    except Exception as e:
        logger.exception("Error analyzing text")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze text"
        )


@router.get("/search", response_model=SearchResponse)
async def search_analyses(
    keyword: str | None = None,
    sentiment: SentimentEnum | None = None,
    limit: int = Query(default=10, ge=1, le=100, description="Maximum number of results to return"),
    offset: int = Query(default=0, ge=0, description="Number of results to skip"),
    db: AsyncSession = Depends(get_db)
):
    """Search analyses by keyword or sentiment."""
    try:
        # Build query
        query = select(Analysis)
        
        # Apply filters
        if keyword:
            query = query.where(
                or_(
                    Analysis.text.ilike(f"%{keyword}%"),
                    Analysis.summary.ilike(f"%{keyword}%"),
                    # Use JSON contains for exact keyword matches (faster than ILIKE)
                    Analysis.keywords.contains([keyword])
                )
            )
        
        if sentiment:
            query = query.where(Analysis.sentiment == sentiment)
        
        # Get total count (optimized)
        count_query = select(func.count()).select_from(Analysis)
        if keyword:
            count_query = count_query.where(
                or_(
                    Analysis.text.ilike(f"%{keyword}%"),
                    Analysis.summary.ilike(f"%{keyword}%"),
                    # Use JSON contains for exact keyword matches (faster than ILIKE)
                    Analysis.keywords.contains([keyword])
                )
            )
        if sentiment:
            count_query = count_query.where(Analysis.sentiment == sentiment)
        
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Apply pagination
        query = query.offset(offset).limit(limit)
        
        # Execute query
        result = await db.execute(query)
        analyses = result.scalars().all()
        
        # Convert to response format
        results = []
        for analysis in analyses:
            # Convert model to dict (metadata already mapped in to_dict())
            analysis_dict = analysis.to_dict()
            # Keywords are already included from to_dict()
            
            results.append(AnalysisResponse(**analysis_dict))
        
        return SearchResponse(
            results=results,
            total=total,
            limit=limit,
            offset=offset
        )
        
    except Exception:
        logger.exception("Error searching analyses")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search analyses"
        )
