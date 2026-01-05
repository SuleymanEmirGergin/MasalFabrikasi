from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict
from pydantic import BaseModel

from app.services.advanced_analytics_service import AdvancedAnalyticsService
from app.services.statistics_analytics_advanced_service import StatisticsAnalyticsAdvancedService
from app.services.story_insights_service import StoryInsightsService
from app.services.reporting_service import ReportingService

router = APIRouter()

advanced_analytics_service = AdvancedAnalyticsService()
statistics_analytics_advanced_service = StatisticsAnalyticsAdvancedService()
story_insights_service = StoryInsightsService()
reporting_service = ReportingService()

# Gelişmiş Analitik
@router.post("/stories/{story_id}/record-scroll")
async def record_scroll(story_id: str, user_id: str, scroll_percentage: float, time_spent: float):
    advanced_analytics_service.record_scroll_depth(story_id, user_id, scroll_percentage, time_spent)
    return {"message": "Kaydedildi"}


@router.get("/stories/{story_id}/scroll-analytics")
async def get_scroll_analytics(story_id: str):
    return advanced_analytics_service.get_scroll_analytics(story_id)

# Raporlama
@router.get("/users/{user_id}/reports/weekly")
async def weekly_report(user_id: str):
    return reporting_service.generate_weekly_report(user_id)


@router.get("/users/{user_id}/reports/monthly")
async def monthly_report(user_id: str):
    return reporting_service.generate_monthly_report(user_id)

# İçgörüler Endpoint'leri
@router.get("/stories/{story_id}/insights")
async def get_story_insights(story_id: str):
    try:
        return await story_insights_service.generate_story_insights(story_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/stories/{story_id_1}/compare-insights/{story_id_2}")
async def compare_insights(story_id_1: str, story_id_2: str):
    try:
        return await story_insights_service.compare_story_insights(story_id_1, story_id_2)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/insights/writing-trends")
async def get_writing_trends(user_id: Optional[str] = None):
    return await story_insights_service.get_writing_trends(user_id)

# Statistics & Analytics Advanced
@router.get("/statistics/reading")
async def get_detailed_reading_statistics(user_id: Optional[str] = None):
    return statistics_analytics_advanced_service.get_detailed_reading_statistics(user_id)


@router.get("/stories/{story_id}/performance")
async def get_story_performance_metrics(story_id: str):
    try:
        return statistics_analytics_advanced_service.get_story_performance_metrics(story_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/analytics/trends")
async def get_trend_analysis(period: str = "week"):
    return statistics_analytics_advanced_service.get_trend_analysis(period)


class QueryAnalyticsRequest(BaseModel):
    metric_type: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    filters: Optional[Dict[str, str]] = None


@router.post("/analytics/query")
async def query_analytics(request: QueryAnalyticsRequest):
    return advanced_analytics_service.query_analytics(
        request.metric_type,
        request.start_date,
        request.end_date,
        request.filters
    )
