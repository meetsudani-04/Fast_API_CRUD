from fastapi import APIRouter, Depends , HTTPException
from uuid import uuid4
from fastapi import status
from sqlalchemy.orm import Session
from api.auth import get_current_user
from db.database import get_db
from db.models import User
from utils.analysis import analyze_with_gemini
from utils.datacollect import fetch_sector_news
import re

from utils.rate_limit import check_rate_limit

router = APIRouter()

@router.get("/get-all-users", tags=["Users"] , status_code=status.HTTP_200_OK)
async def get_all_users(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
    
):
    users = db.query(User).all()
    return {"status": "success", "message": "users fetched successfully", "data": users}


@router.get("/analyze/{sector}",
            tags=["Trade Analysis"],
            summary="Analyze trade opportunities for a sector",
            description="Returns markdown report with current market analysis for Indian sectors",
            responses={
                200: {"description": "Analysis report generated successfully"},
                400: {"description": "Invalid sector name"},
                401: {"description": "Unauthorized"},
                429: {"description": "Rate limit exceeded"},
                500: {"description": "Internal server error"}
            })
async def analyze_sector(
    sector: str,
    user = Depends(get_current_user),
):
    # Validate input
    validated_sector = sector
    
    # Check rate limit
    check_rate_limit(user.email)
    
    # Get news - FIX: Convert list to string
    news_data = await fetch_sector_news(validated_sector)
    news = "\n\n".join(news_data) if isinstance(news_data, list) else news_data
    
    # Analyze with Gemini
    markdown = await analyze_with_gemini(news, validated_sector)
    
    return {"report_md": markdown}