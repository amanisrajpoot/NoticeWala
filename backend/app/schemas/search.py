"""
Search schemas
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class SearchRequest(BaseModel):
    """Schema for search requests"""
    query: str = Field(..., description="Search query")
    limit: int = Field(20, ge=1, le=100, description="Maximum number of results")
    filters: Optional[Dict[str, Any]] = Field(None, description="Additional filters")
    search_type: str = Field("semantic", description="Type of search: semantic, natural_language, advanced_filter")


class SearchMetadata(BaseModel):
    """Schema for search metadata"""
    query: str = Field(..., description="Original search query")
    search_type: str = Field(..., description="Type of search performed")
    similarity_score: Optional[float] = Field(None, description="Similarity score for semantic search")
    personalized: bool = Field(False, description="Whether results were personalized")
    intent: Optional[str] = Field(None, description="Detected intent for natural language search")
    parsed_terms: Optional[List[str]] = Field(None, description="Parsed search terms")
    filters_applied: Optional[Dict[str, Any]] = Field(None, description="Filters applied to search")
    personalization_boost: Optional[float] = Field(None, description="Personalization boost score")


class SearchResult(BaseModel):
    """Schema for individual search results"""
    announcement: Dict[str, Any] = Field(..., description="Announcement data")
    search_metadata: SearchMetadata = Field(..., description="Search metadata for this result")


class SearchResponse(BaseModel):
    """Schema for search responses"""
    success: bool = Field(..., description="Whether the search was successful")
    query: str = Field(..., description="Original search query")
    results: List[SearchResult] = Field(..., description="Search results")
    total_count: int = Field(..., description="Total number of results")
    search_type: str = Field(..., description="Type of search performed")
    execution_time_ms: Optional[float] = Field(None, description="Search execution time in milliseconds")


class SearchSuggestion(BaseModel):
    """Schema for search suggestions"""
    suggestion: str = Field(..., description="Suggested search term")
    type: str = Field(..., description="Type of suggestion: title, category, tag")
    frequency: Optional[int] = Field(None, description="Frequency of this suggestion")


class SearchSuggestionResponse(BaseModel):
    """Schema for search suggestion responses"""
    success: bool = Field(..., description="Whether the request was successful")
    query: str = Field(..., description="Original partial query")
    suggestions: List[str] = Field(..., description="List of suggestions")
    total_count: int = Field(..., description="Total number of suggestions")


class SearchAnalytics(BaseModel):
    """Schema for search analytics"""
    total_searches: int = Field(..., description="Total number of searches")
    unique_users: int = Field(..., description="Number of unique users who searched")
    popular_queries: List[Dict[str, Any]] = Field(..., description="Popular search queries")
    search_success_rate: float = Field(..., description="Search success rate")
    avg_results_per_search: float = Field(..., description="Average results per search")
    top_categories_searched: List[Dict[str, Any]] = Field(..., description="Top categories searched")
    search_trends: Dict[str, Any] = Field(..., description="Search trends over time")
    user_specific: bool = Field(..., description="Whether analytics are user-specific")


class SearchAnalyticsResponse(BaseModel):
    """Schema for search analytics responses"""
    success: bool = Field(..., description="Whether the request was successful")
    analytics: SearchAnalytics = Field(..., description="Search analytics data")
    period_days: int = Field(..., description="Number of days analyzed")
    user_specific: bool = Field(..., description="Whether analytics are user-specific")


class TrendingSearch(BaseModel):
    """Schema for trending searches"""
    query: str = Field(..., description="Search query")
    count: int = Field(..., description="Number of searches")
    trend: str = Field(..., description="Trend direction: up, down, stable")


class PopularCategory(BaseModel):
    """Schema for popular categories"""
    category: str = Field(..., description="Category name")
    count: int = Field(..., description="Number of searches for this category")


class SearchHistoryItem(BaseModel):
    """Schema for search history items"""
    query: str = Field(..., description="Search query")
    timestamp: str = Field(..., description="Timestamp of the search")
    results_count: int = Field(..., description="Number of results returned")
    search_type: str = Field(..., description="Type of search performed")


class SearchFilter(BaseModel):
    """Schema for search filters"""
    categories: Optional[List[str]] = Field(None, description="Filter by categories")
    exam_types: Optional[List[str]] = Field(None, description="Filter by exam types")
    locations: Optional[List[str]] = Field(None, description="Filter by locations")
    date_from: Optional[datetime] = Field(None, description="Filter by date from")
    date_to: Optional[datetime] = Field(None, description="Filter by date to")
    min_priority: Optional[float] = Field(None, description="Minimum priority score")
    difficulty_levels: Optional[List[str]] = Field(None, description="Filter by difficulty levels")
    text_search: Optional[str] = Field(None, description="Text search within content")
    sort_by: Optional[str] = Field("created_at", description="Sort by field")
    sort_order: Optional[str] = Field("desc", description="Sort order: asc, desc")


class AdvancedSearchRequest(BaseModel):
    """Schema for advanced search requests"""
    filters: SearchFilter = Field(..., description="Search filters")
    limit: int = Field(20, ge=1, le=100, description="Maximum number of results")
    user_id: Optional[str] = Field(None, description="User ID for personalization")


class SearchIntent(BaseModel):
    """Schema for search intent detection"""
    intent: str = Field(..., description="Detected intent")
    confidence: float = Field(..., description="Confidence score for intent detection")
    entities: List[Dict[str, Any]] = Field(..., description="Extracted entities")
    filters: Dict[str, Any] = Field(..., description="Extracted filters")


class SearchPerformanceMetrics(BaseModel):
    """Schema for search performance metrics"""
    avg_response_time_ms: float = Field(..., description="Average response time in milliseconds")
    cache_hit_rate: float = Field(..., description="Cache hit rate")
    error_rate: float = Field(..., description="Error rate")
    throughput_per_second: float = Field(..., description="Searches per second")
    memory_usage_mb: float = Field(..., description="Memory usage in MB")


class SearchServiceStatus(BaseModel):
    """Schema for search service status"""
    service_active: bool = Field(..., description="Whether the service is active")
    sentence_transformer_available: bool = Field(..., description="Whether sentence transformer is available")
    tfidf_vectorizer_available: bool = Field(..., description="Whether TF-IDF vectorizer is available")
    search_types_supported: List[str] = Field(..., description="Supported search types")
    features: List[str] = Field(..., description="Available features")
    performance_metrics: Optional[SearchPerformanceMetrics] = Field(None, description="Performance metrics")


class SearchQueryAnalysis(BaseModel):
    """Schema for search query analysis"""
    query: str = Field(..., description="Original query")
    tokens: List[str] = Field(..., description="Tokenized query")
    entities: List[Dict[str, Any]] = Field(..., description="Extracted entities")
    intent: str = Field(..., description="Detected intent")
    confidence: float = Field(..., description="Confidence score")
    suggestions: List[str] = Field(..., description="Query suggestions")
    filters: Dict[str, Any] = Field(..., description="Extracted filters")


class SearchResultRanking(BaseModel):
    """Schema for search result ranking"""
    announcement_id: str = Field(..., description="Announcement ID")
    relevance_score: float = Field(..., description="Relevance score")
    personalization_score: float = Field(..., description="Personalization score")
    recency_score: float = Field(..., description="Recency score")
    popularity_score: float = Field(..., description="Popularity score")
    final_score: float = Field(..., description="Final ranking score")
    ranking_factors: Dict[str, Any] = Field(..., description="Factors that influenced ranking")
