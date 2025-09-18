"""
Advanced Search Service for semantic search and natural language queries
"""

import re
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import structlog
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func, text
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.models.announcement import Announcement
from app.models.user import User
from app.core.database import get_db

logger = structlog.get_logger()


class SearchService:
    """Advanced search service with semantic search capabilities"""
    
    def __init__(self):
        self.sentence_transformer = None
        self.tfidf_vectorizer = None
        self.search_cache = {}
        
        # Initialize sentence transformer for semantic search
        try:
            self.sentence_transformer = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Sentence transformer initialized for search")
        except Exception as e:
            logger.error(f"Failed to initialize sentence transformer: {e}")
        
        # Initialize TF-IDF vectorizer
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
    
    async def semantic_search(
        self,
        query: str,
        user_id: Optional[str] = None,
        limit: int = 20,
        filters: Optional[Dict[str, Any]] = None,
        db: Session = None
    ) -> List[Dict[str, Any]]:
        """Perform semantic search using vector similarity"""
        
        try:
            # Get candidate announcements
            candidates = await self._get_search_candidates(filters, db)
            
            if not candidates:
                return []
            
            # Calculate semantic similarity
            if self.sentence_transformer:
                results = await self._semantic_similarity_search(query, candidates, limit)
            else:
                results = await self._tfidf_similarity_search(query, candidates, limit)
            
            # Apply user personalization if user_id provided
            if user_id:
                results = await self._apply_personalization_boost(user_id, results, db)
            
            # Add search metadata
            for result in results:
                result["search_metadata"] = {
                    "query": query,
                    "search_type": "semantic",
                    "similarity_score": result.get("similarity_score", 0),
                    "personalized": user_id is not None
                }
            
            logger.info(
                "Semantic search completed",
                query=query,
                results_count=len(results),
                user_id=user_id
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return []
    
    async def natural_language_search(
        self,
        query: str,
        user_id: Optional[str] = None,
        limit: int = 20,
        db: Session = None
    ) -> List[Dict[str, Any]]:
        """Process natural language queries and return relevant results"""
        
        try:
            # Parse natural language query
            parsed_query = await self._parse_natural_language_query(query)
            
            # Extract search terms and filters
            search_terms = parsed_query.get("search_terms", [])
            filters = parsed_query.get("filters", {})
            intent = parsed_query.get("intent", "search")
            
            # Perform search based on intent
            if intent == "search":
                results = await self.semantic_search(
                    query=" ".join(search_terms),
                    user_id=user_id,
                    limit=limit,
                    filters=filters,
                    db=db
                )
            elif intent == "find_exams":
                results = await self._find_exams_by_criteria(search_terms, filters, limit, db)
            elif intent == "find_deadlines":
                results = await self._find_upcoming_deadlines(search_terms, filters, limit, db)
            elif intent == "find_by_location":
                results = await self._find_by_location(search_terms, filters, limit, db)
            else:
                results = await self.semantic_search(
                    query=" ".join(search_terms),
                    user_id=user_id,
                    limit=limit,
                    filters=filters,
                    db=db
                )
            
            # Add natural language metadata
            for result in results:
                result["search_metadata"] = {
                    "query": query,
                    "search_type": "natural_language",
                    "intent": intent,
                    "parsed_terms": search_terms,
                    "personalized": user_id is not None
                }
            
            logger.info(
                "Natural language search completed",
                query=query,
                intent=intent,
                results_count=len(results)
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Natural language search failed: {e}")
            return []
    
    async def advanced_filter_search(
        self,
        filters: Dict[str, Any],
        user_id: Optional[str] = None,
        limit: int = 20,
        db: Session = None
    ) -> List[Dict[str, Any]]:
        """Advanced search with multiple filters"""
        
        try:
            # Build database query with filters
            query = db.query(Announcement)
            
            # Apply filters
            conditions = []
            
            # Category filter
            if filters.get("categories"):
                conditions.append(Announcement.categories.op('&&')(filters["categories"]))
            
            # Exam type filter
            if filters.get("exam_types"):
                conditions.append(Announcement.exam_type.in_(filters["exam_types"]))
            
            # Location filter
            if filters.get("locations"):
                location_conditions = []
                for location in filters["locations"]:
                    location_conditions.append(
                        Announcement.location.op('->>')('state') == location
                    )
                    location_conditions.append(
                        Announcement.location.op('->>')('country') == location
                    )
                conditions.append(or_(*location_conditions))
            
            # Date range filter
            if filters.get("date_from"):
                conditions.append(Announcement.created_at >= filters["date_from"])
            
            if filters.get("date_to"):
                conditions.append(Announcement.created_at <= filters["date_to"])
            
            # Priority score filter
            if filters.get("min_priority"):
                conditions.append(Announcement.priority_score >= filters["min_priority"])
            
            # Difficulty level filter
            if filters.get("difficulty_levels"):
                conditions.append(Announcement.difficulty_level.in_(filters["difficulty_levels"]))
            
            # Text search filter
            if filters.get("text_search"):
                text_conditions = []
                search_term = f"%{filters['text_search']}%"
                text_conditions.append(Announcement.title.ilike(search_term))
                text_conditions.append(Announcement.summary.ilike(search_term))
                text_conditions.append(Announcement.content.ilike(search_term))
                conditions.append(or_(*text_conditions))
            
            # Apply conditions
            if conditions:
                query = query.filter(and_(*conditions))
            
            # Apply sorting
            sort_by = filters.get("sort_by", "created_at")
            sort_order = filters.get("sort_order", "desc")
            
            if sort_by == "created_at":
                if sort_order == "desc":
                    query = query.order_by(desc(Announcement.created_at))
                else:
                    query = query.order_by(Announcement.created_at)
            elif sort_by == "priority_score":
                if sort_order == "desc":
                    query = query.order_by(desc(Announcement.priority_score))
                else:
                    query = query.order_by(Announcement.priority_score)
            elif sort_by == "title":
                if sort_order == "desc":
                    query = query.order_by(desc(Announcement.title))
                else:
                    query = query.order_by(Announcement.title)
            
            # Execute query
            announcements = query.limit(limit).all()
            
            # Convert to results
            results = []
            for announcement in announcements:
                result = {
                    "announcement": announcement.__dict__,
                    "search_metadata": {
                        "search_type": "advanced_filter",
                        "filters_applied": filters,
                        "personalized": user_id is not None
                    }
                }
                results.append(result)
            
            # Apply user personalization if user_id provided
            if user_id:
                results = await self._apply_personalization_boost(user_id, results, db)
            
            logger.info(
                "Advanced filter search completed",
                filters=filters,
                results_count=len(results),
                user_id=user_id
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Advanced filter search failed: {e}")
            return []
    
    async def get_search_suggestions(
        self,
        query: str,
        limit: int = 10,
        db: Session = None
    ) -> List[str]:
        """Get search suggestions based on partial query"""
        
        try:
            suggestions = []
            
            # Get suggestions from announcement titles
            title_suggestions = db.query(Announcement.title).filter(
                Announcement.title.ilike(f"%{query}%")
            ).distinct().limit(limit // 2).all()
            
            for title in title_suggestions:
                suggestions.append(title[0])
            
            # Get suggestions from categories
            category_suggestions = db.query(Announcement.categories).filter(
                Announcement.categories.isnot(None)
            ).distinct().limit(limit // 4).all()
            
            for categories in category_suggestions:
                if categories[0]:
                    for category in categories[0]:
                        if query.lower() in category.lower():
                            suggestions.append(category)
            
            # Get suggestions from tags
            tag_suggestions = db.query(Announcement.tags).filter(
                Announcement.tags.isnot(None)
            ).distinct().limit(limit // 4).all()
            
            for tags in tag_suggestions:
                if tags[0]:
                    for tag in tags[0]:
                        if query.lower() in tag.lower():
                            suggestions.append(tag)
            
            # Remove duplicates and limit
            suggestions = list(set(suggestions))[:limit]
            
            logger.info(
                "Search suggestions generated",
                query=query,
                suggestions_count=len(suggestions)
            )
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Failed to get search suggestions: {e}")
            return []
    
    async def get_search_analytics(
        self,
        user_id: Optional[str] = None,
        days: int = 30,
        db: Session = None
    ) -> Dict[str, Any]:
        """Get search analytics and insights"""
        
        try:
            # Get search data from last N days
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # This would require a search_logs table in a real implementation
            # For now, return mock analytics
            analytics = {
                "total_searches": 0,
                "unique_users": 0,
                "popular_queries": [],
                "search_success_rate": 0.0,
                "avg_results_per_search": 0.0,
                "top_categories_searched": [],
                "search_trends": {},
                "user_specific": user_id is not None
            }
            
            logger.info(
                "Search analytics generated",
                user_id=user_id,
                days=days
            )
            
            return analytics
            
        except Exception as e:
            logger.error(f"Failed to get search analytics: {e}")
            return {}
    
    async def _get_search_candidates(
        self,
        filters: Optional[Dict[str, Any]],
        db: Session
    ) -> List[Announcement]:
        """Get candidate announcements for search"""
        
        query = db.query(Announcement)
        
        if filters:
            conditions = []
            
            # Apply basic filters
            if filters.get("categories"):
                conditions.append(Announcement.categories.op('&&')(filters["categories"]))
            
            if filters.get("exam_types"):
                conditions.append(Announcement.exam_type.in_(filters["exam_types"]))
            
            if conditions:
                query = query.filter(and_(*conditions))
        
        # Get recent announcements (last 90 days)
        query = query.filter(
            Announcement.created_at >= datetime.utcnow() - timedelta(days=90)
        )
        
        return query.all()
    
    async def _semantic_similarity_search(
        self,
        query: str,
        candidates: List[Announcement],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Perform semantic similarity search using sentence transformers"""
        
        try:
            # Prepare texts for embedding
            candidate_texts = []
            for announcement in candidates:
                text = f"{announcement.title} {announcement.summary or ''}"
                candidate_texts.append(text)
            
            # Get embeddings
            query_embedding = self.sentence_transformer.encode([query])
            candidate_embeddings = self.sentence_transformer.encode(candidate_texts)
            
            # Calculate similarities
            similarities = cosine_similarity(query_embedding, candidate_embeddings)[0]
            
            # Create results
            results = []
            for i, (announcement, similarity) in enumerate(zip(candidates, similarities)):
                results.append({
                    "announcement": announcement.__dict__,
                    "similarity_score": float(similarity)
                })
            
            # Sort by similarity and return top results
            results.sort(key=lambda x: x["similarity_score"], reverse=True)
            
            return results[:limit]
            
        except Exception as e:
            logger.error(f"Semantic similarity search failed: {e}")
            return []
    
    async def _tfidf_similarity_search(
        self,
        query: str,
        candidates: List[Announcement],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Fallback TF-IDF similarity search"""
        
        try:
            # Prepare texts
            candidate_texts = []
            for announcement in candidates:
                text = f"{announcement.title} {announcement.summary or ''}"
                candidate_texts.append(text)
            
            # Fit TF-IDF vectorizer
            all_texts = [query] + candidate_texts
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(all_texts)
            
            # Calculate similarities
            query_vector = tfidf_matrix[0:1]
            candidate_vectors = tfidf_matrix[1:]
            similarities = cosine_similarity(query_vector, candidate_vectors)[0]
            
            # Create results
            results = []
            for i, (announcement, similarity) in enumerate(zip(candidates, similarities)):
                results.append({
                    "announcement": announcement.__dict__,
                    "similarity_score": float(similarity)
                })
            
            # Sort by similarity and return top results
            results.sort(key=lambda x: x["similarity_score"], reverse=True)
            
            return results[:limit]
            
        except Exception as e:
            logger.error(f"TF-IDF similarity search failed: {e}")
            return []
    
    async def _parse_natural_language_query(self, query: str) -> Dict[str, Any]:
        """Parse natural language query to extract intent and filters"""
        
        query_lower = query.lower()
        
        # Define patterns for different intents
        intent_patterns = {
            "find_exams": [
                r"find.*exam", r"show.*exam", r"list.*exam",
                r"what.*exam", r"which.*exam"
            ],
            "find_deadlines": [
                r"deadline", r"last date", r"closing date",
                r"when.*close", r"expire"
            ],
            "find_by_location": [
                r"in\s+(\w+)", r"at\s+(\w+)", r"location.*(\w+)",
                r"state.*(\w+)", r"city.*(\w+)"
            ]
        }
        
        # Determine intent
        intent = "search"  # default
        for intent_name, patterns in intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    intent = intent_name
                    break
            if intent != "search":
                break
        
        # Extract search terms
        search_terms = []
        
        # Remove common stop words
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        words = re.findall(r'\b\w+\b', query_lower)
        search_terms = [word for word in words if word not in stop_words]
        
        # Extract filters based on intent
        filters = {}
        
        if intent == "find_by_location":
            # Extract location from query
            location_match = re.search(r"in\s+(\w+)|at\s+(\w+)|location.*(\w+)|state.*(\w+)|city.*(\w+)", query_lower)
            if location_match:
                location = location_match.group(1) or location_match.group(2) or location_match.group(3) or location_match.group(4) or location_match.group(5)
                filters["locations"] = [location]
        
        # Extract date-related filters
        if "this week" in query_lower:
            filters["date_from"] = datetime.utcnow() - timedelta(days=7)
        elif "this month" in query_lower:
            filters["date_from"] = datetime.utcnow() - timedelta(days=30)
        elif "recent" in query_lower:
            filters["date_from"] = datetime.utcnow() - timedelta(days=7)
        
        # Extract category filters
        category_keywords = {
            "upsc": ["upsc", "civil services", "ias"],
            "ssc": ["ssc", "staff selection", "cgl", "chsl"],
            "banking": ["banking", "ibps", "sbi", "po", "clerk"],
            "engineering": ["engineering", "gate", "jee", "neet"],
            "railway": ["railway", "rrb", "ntpc"],
            "defense": ["army", "navy", "air force", "defense"]
        }
        
        detected_categories = []
        for category, keywords in category_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                detected_categories.append(category)
        
        if detected_categories:
            filters["categories"] = detected_categories
        
        return {
            "search_terms": search_terms,
            "filters": filters,
            "intent": intent
        }
    
    async def _find_exams_by_criteria(
        self,
        search_terms: List[str],
        filters: Dict[str, Any],
        limit: int,
        db: Session
    ) -> List[Dict[str, Any]]:
        """Find exams based on specific criteria"""
        
        query = db.query(Announcement)
        
        # Add text search
        if search_terms:
            text_conditions = []
            for term in search_terms:
                text_conditions.append(Announcement.title.ilike(f"%{term}%"))
                text_conditions.append(Announcement.summary.ilike(f"%{term}%"))
            query = query.filter(or_(*text_conditions))
        
        # Apply filters
        conditions = []
        if filters.get("categories"):
            conditions.append(Announcement.categories.op('&&')(filters["categories"]))
        
        if conditions:
            query = query.filter(and_(*conditions))
        
        # Get results
        announcements = query.order_by(desc(Announcement.created_at)).limit(limit).all()
        
        results = []
        for announcement in announcements:
            results.append({
                "announcement": announcement.__dict__,
                "search_metadata": {
                    "search_type": "find_exams",
                    "criteria": search_terms,
                    "filters": filters
                }
            })
        
        return results
    
    async def _find_upcoming_deadlines(
        self,
        search_terms: List[str],
        filters: Dict[str, Any],
        limit: int,
        db: Session
    ) -> List[Dict[str, Any]]:
        """Find announcements with upcoming deadlines"""
        
        query = db.query(Announcement).filter(
            Announcement.application_deadline.isnot(None),
            Announcement.application_deadline > datetime.utcnow()
        )
        
        # Add text search
        if search_terms:
            text_conditions = []
            for term in search_terms:
                text_conditions.append(Announcement.title.ilike(f"%{term}%"))
            query = query.filter(or_(*text_conditions))
        
        # Apply filters
        conditions = []
        if filters.get("categories"):
            conditions.append(Announcement.categories.op('&&')(filters["categories"]))
        
        if conditions:
            query = query.filter(and_(*conditions))
        
        # Sort by deadline
        announcements = query.order_by(Announcement.application_deadline).limit(limit).all()
        
        results = []
        for announcement in announcements:
            results.append({
                "announcement": announcement.__dict__,
                "search_metadata": {
                    "search_type": "find_deadlines",
                    "deadline_approaching": True,
                    "days_until_deadline": (announcement.application_deadline - datetime.utcnow()).days
                }
            })
        
        return results
    
    async def _find_by_location(
        self,
        search_terms: List[str],
        filters: Dict[str, Any],
        limit: int,
        db: Session
    ) -> List[Dict[str, Any]]:
        """Find announcements by location"""
        
        query = db.query(Announcement)
        
        # Location filter
        if filters.get("locations"):
            location_conditions = []
            for location in filters["locations"]:
                location_conditions.append(
                    Announcement.location.op('->>')('state') == location
                )
                location_conditions.append(
                    Announcement.location.op('->>')('country') == location
                )
            query = query.filter(or_(*location_conditions))
        
        # Add text search
        if search_terms:
            text_conditions = []
            for term in search_terms:
                text_conditions.append(Announcement.title.ilike(f"%{term}%"))
            query = query.filter(or_(*text_conditions))
        
        # Get results
        announcements = query.order_by(desc(Announcement.created_at)).limit(limit).all()
        
        results = []
        for announcement in announcements:
            results.append({
                "announcement": announcement.__dict__,
                "search_metadata": {
                    "search_type": "find_by_location",
                    "location": filters.get("locations", []),
                    "search_terms": search_terms
                }
            })
        
        return results
    
    async def _apply_personalization_boost(
        self,
        user_id: str,
        results: List[Dict[str, Any]],
        db: Session
    ) -> List[Dict[str, Any]]:
        """Apply personalization boost to search results"""
        
        try:
            # Import here to avoid circular imports
            from app.services.personalization_service import personalization_service
            
            # Get user profile
            user_profile = await personalization_service._get_user_profile(user_id, db)
            
            # Boost scores based on user preferences
            for result in results:
                announcement = result["announcement"]
                if isinstance(announcement, dict):
                    announcement_obj = type('Announcement', (), announcement)()
                else:
                    announcement_obj = announcement
                
                # Calculate personalization boost
                boost = await personalization_service._calculate_recommendation_score(
                    user_profile, announcement_obj, db
                )
                
                # Apply boost to similarity score
                if "similarity_score" in result:
                    result["similarity_score"] = result["similarity_score"] + (boost * 0.1)
                else:
                    result["similarity_score"] = boost * 0.1
                
                # Add personalization metadata
                result["personalization_boost"] = boost
                result["personalized"] = True
            
            # Re-sort by boosted scores
            results.sort(key=lambda x: x.get("similarity_score", 0), reverse=True)
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to apply personalization boost: {e}")
            return results


# Global search service instance
search_service = SearchService()
