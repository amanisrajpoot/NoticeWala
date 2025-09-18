"""
Personalization Service for user preference learning and recommendations
"""

import json
import math
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import structlog
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func

from app.models.user import User
from app.models.announcement import Announcement
from app.models.user import Subscription
from app.core.database import get_db

logger = structlog.get_logger()


class PersonalizationService:
    """Service for user personalization and recommendation engine"""
    
    def __init__(self):
        self.user_profiles = {}  # Cache for user profiles
        self.content_features = {}  # Cache for content features
        self.similarity_cache = {}  # Cache for user similarities
    
    async def learn_user_preferences(
        self, 
        user_id: str, 
        interaction_type: str, 
        announcement_id: str,
        db: Session
    ) -> Dict[str, Any]:
        """Learn user preferences from interactions"""
        
        try:
            # Get or create user profile
            user_profile = await self._get_user_profile(user_id, db)
            
            # Update interaction history
            interaction = {
                "type": interaction_type,  # view, click, bookmark, subscribe, dismiss
                "announcement_id": announcement_id,
                "timestamp": datetime.utcnow().isoformat(),
                "weight": self._get_interaction_weight(interaction_type)
            }
            
            if "interactions" not in user_profile:
                user_profile["interactions"] = []
            
            user_profile["interactions"].append(interaction)
            
            # Keep only last 1000 interactions
            user_profile["interactions"] = user_profile["interactions"][-1000:]
            
            # Update preference scores
            await self._update_preference_scores(user_id, user_profile, db)
            
            # Save updated profile
            await self._save_user_profile(user_id, user_profile, db)
            
            logger.info(
                "User preference learned",
                user_id=user_id,
                interaction_type=interaction_type,
                announcement_id=announcement_id
            )
            
            return {
                "success": True,
                "user_id": user_id,
                "interaction_recorded": True,
                "profile_updated": True
            }
            
        except Exception as e:
            logger.error(f"Failed to learn user preferences: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_personalized_recommendations(
        self, 
        user_id: str, 
        limit: int = 20,
        db: Session = None
    ) -> List[Dict[str, Any]]:
        """Get personalized recommendations for a user"""
        
        try:
            # Get user profile
            user_profile = await self._get_user_profile(user_id, db)
            
            # Get candidate announcements
            candidates = await self._get_candidate_announcements(user_id, limit * 3, db)
            
            # Score candidates based on user preferences
            scored_candidates = []
            for announcement in candidates:
                score = await self._calculate_recommendation_score(
                    user_profile, announcement, db
                )
                scored_candidates.append({
                    "announcement": announcement,
                    "score": score,
                    "reasons": await self._get_recommendation_reasons(
                        user_profile, announcement
                    )
                })
            
            # Sort by score and return top recommendations
            scored_candidates.sort(key=lambda x: x["score"], reverse=True)
            
            recommendations = scored_candidates[:limit]
            
            logger.info(
                "Generated personalized recommendations",
                user_id=user_id,
                total_candidates=len(candidates),
                recommendations_count=len(recommendations)
            )
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to get personalized recommendations: {e}")
            return []
    
    async def get_content_based_recommendations(
        self, 
        user_id: str, 
        content_id: str,
        limit: int = 10,
        db: Session = None
    ) -> List[Dict[str, Any]]:
        """Get content-based recommendations based on a specific announcement"""
        
        try:
            # Get the source announcement
            source_announcement = db.query(Announcement).filter(
                Announcement.id == content_id
            ).first()
            
            if not source_announcement:
                return []
            
            # Find similar announcements
            similar_announcements = await self._find_similar_announcements(
                source_announcement, limit, db
            )
            
            # Score based on user preferences
            user_profile = await self._get_user_profile(user_id, db)
            scored_recommendations = []
            
            for announcement in similar_announcements:
                score = await self._calculate_recommendation_score(
                    user_profile, announcement, db
                )
                scored_recommendations.append({
                    "announcement": announcement,
                    "score": score,
                    "similarity_reason": "Similar content and categories"
                })
            
            scored_recommendations.sort(key=lambda x: x["score"], reverse=True)
            
            return scored_recommendations[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get content-based recommendations: {e}")
            return []
    
    async def get_collaborative_recommendations(
        self, 
        user_id: str, 
        limit: int = 10,
        db: Session = None
    ) -> List[Dict[str, Any]]:
        """Get collaborative filtering recommendations"""
        
        try:
            # Find similar users
            similar_users = await self._find_similar_users(user_id, db)
            
            if not similar_users:
                return []
            
            # Get announcements liked by similar users
            recommendations = await self._get_recommendations_from_similar_users(
                user_id, similar_users, limit, db
            )
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to get collaborative recommendations: {e}")
            return []
    
    async def _get_user_profile(self, user_id: str, db: Session) -> Dict[str, Any]:
        """Get or create user profile"""
        
        if user_id in self.user_profiles:
            return self.user_profiles[user_id]
        
        # Get user from database
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            # Create default profile
            profile = self._create_default_profile()
        else:
            # Load existing profile from user preferences
            profile = user.preferences or self._create_default_profile()
        
        # Ensure profile has required fields
        profile = self._ensure_profile_structure(profile)
        
        # Cache profile
        self.user_profiles[user_id] = profile
        
        return profile
    
    def _create_default_profile(self) -> Dict[str, Any]:
        """Create default user profile"""
        return {
            "preferences": {
                "categories": [],
                "exam_types": [],
                "locations": [],
                "keywords": [],
                "difficulty_levels": [],
                "time_preferences": {
                    "morning": 0.5,
                    "afternoon": 0.5,
                    "evening": 0.5,
                    "night": 0.3
                }
            },
            "interactions": [],
            "preference_scores": {
                "categories": {},
                "exam_types": {},
                "locations": {},
                "keywords": {},
                "difficulty_levels": {},
                "sources": {}
            },
            "behavioral_patterns": {
                "avg_session_duration": 0,
                "preferred_content_length": "medium",
                "interaction_frequency": "medium",
                "notification_preferences": "immediate"
            },
            "last_updated": datetime.utcnow().isoformat()
        }
    
    def _ensure_profile_structure(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure profile has all required fields"""
        default_profile = self._create_default_profile()
        
        for key, default_value in default_profile.items():
            if key not in profile:
                profile[key] = default_value
            elif isinstance(default_value, dict) and isinstance(profile[key], dict):
                for sub_key, sub_default in default_value.items():
                    if sub_key not in profile[key]:
                        profile[key][sub_key] = sub_default
        
        return profile
    
    def _get_interaction_weight(self, interaction_type: str) -> float:
        """Get weight for different interaction types"""
        weights = {
            "view": 0.1,
            "click": 0.3,
            "bookmark": 0.8,
            "subscribe": 1.0,
            "dismiss": -0.5,
            "share": 0.6,
            "download": 0.7
        }
        return weights.get(interaction_type, 0.1)
    
    async def _update_preference_scores(
        self, 
        user_id: str, 
        user_profile: Dict[str, Any],
        db: Session
    ):
        """Update preference scores based on interactions"""
        
        # Get recent interactions (last 30 days)
        recent_interactions = [
            interaction for interaction in user_profile.get("interactions", [])
            if self._is_recent_interaction(interaction)
        ]
        
        if not recent_interactions:
            return
        
        # Get announcements for these interactions
        announcement_ids = [i["announcement_id"] for i in recent_interactions]
        announcements = db.query(Announcement).filter(
            Announcement.id.in_(announcement_ids)
        ).all()
        
        announcement_map = {str(a.id): a for a in announcements}
        
        # Update preference scores
        preference_scores = user_profile.get("preference_scores", {})
        
        for interaction in recent_interactions:
            announcement_id = interaction["announcement_id"]
            weight = interaction["weight"]
            
            if announcement_id not in announcement_map:
                continue
            
            announcement = announcement_map[announcement_id]
            
            # Update category scores
            if announcement.categories:
                for category in announcement.categories:
                    current_score = preference_scores.get("categories", {}).get(category, 0)
                    preference_scores.setdefault("categories", {})[category] = current_score + weight
            
            # Update exam type scores
            if announcement.exam_type:
                current_score = preference_scores.get("exam_types", {}).get(announcement.exam_type, 0)
                preference_scores.setdefault("exam_types", {})[announcement.exam_type] = current_score + weight
            
            # Update location scores
            if announcement.location:
                location = announcement.location.get("state") or announcement.location.get("country")
                if location:
                    current_score = preference_scores.get("locations", {}).get(location, 0)
                    preference_scores.setdefault("locations", {})[location] = current_score + weight
            
            # Update keyword scores
            if announcement.tags:
                for tag in announcement.tags:
                    current_score = preference_scores.get("keywords", {}).get(tag, 0)
                    preference_scores.setdefault("keywords", {})[tag] = current_score + weight
        
        user_profile["preference_scores"] = preference_scores
        user_profile["last_updated"] = datetime.utcnow().isoformat()
    
    def _is_recent_interaction(self, interaction: Dict[str, Any]) -> bool:
        """Check if interaction is recent (within 30 days)"""
        try:
            interaction_time = datetime.fromisoformat(interaction["timestamp"])
            return (datetime.utcnow() - interaction_time).days <= 30
        except:
            return False
    
    async def _get_candidate_announcements(
        self, 
        user_id: str, 
        limit: int,
        db: Session
    ) -> List[Announcement]:
        """Get candidate announcements for recommendations"""
        
        # Get user subscriptions to filter candidates
        user_subscriptions = db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.is_active == True
        ).all()
        
        # Build filter conditions
        conditions = []
        
        for subscription in user_subscriptions:
            if subscription.filters:
                filters = subscription.filters
                
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
        
        # If no subscriptions, get recent announcements
        if not conditions:
            conditions.append(Announcement.created_at >= datetime.utcnow() - timedelta(days=30))
        
        # Get candidates
        query = db.query(Announcement).filter(or_(*conditions) if conditions else True)
        candidates = query.order_by(desc(Announcement.created_at)).limit(limit).all()
        
        return candidates
    
    async def _calculate_recommendation_score(
        self, 
        user_profile: Dict[str, Any], 
        announcement: Announcement,
        db: Session
    ) -> float:
        """Calculate recommendation score for an announcement"""
        
        score = 0.0
        preference_scores = user_profile.get("preference_scores", {})
        
        # Category scoring
        if announcement.categories:
            category_scores = preference_scores.get("categories", {})
            for category in announcement.categories:
                score += category_scores.get(category, 0) * 0.3
        
        # Exam type scoring
        if announcement.exam_type:
            exam_type_scores = preference_scores.get("exam_types", {})
            score += exam_type_scores.get(announcement.exam_type, 0) * 0.4
        
        # Location scoring
        if announcement.location:
            location_scores = preference_scores.get("locations", {})
            location = announcement.location.get("state") or announcement.location.get("country")
            if location:
                score += location_scores.get(location, 0) * 0.2
        
        # Keyword scoring
        if announcement.tags:
            keyword_scores = preference_scores.get("keywords", {})
            for tag in announcement.tags:
                score += keyword_scores.get(tag, 0) * 0.1
        
        # Recency scoring (newer announcements get higher scores)
        days_old = (datetime.utcnow() - announcement.created_at).days
        recency_score = max(0, 1 - (days_old / 30))  # Decay over 30 days
        score += recency_score * 0.2
        
        # Priority score from announcement
        if announcement.priority_score:
            score += (announcement.priority_score / 10) * 0.3
        
        return max(0, score)  # Ensure non-negative score
    
    async def _get_recommendation_reasons(
        self, 
        user_profile: Dict[str, Any], 
        announcement: Announcement
    ) -> List[str]:
        """Get reasons why this announcement was recommended"""
        
        reasons = []
        preference_scores = user_profile.get("preference_scores", {})
        
        # Check category matches
        if announcement.categories:
            category_scores = preference_scores.get("categories", {})
            top_categories = sorted(
                category_scores.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:3]
            
            for category, score in top_categories:
                if category in announcement.categories and score > 0:
                    reasons.append(f"Matches your interest in {category}")
        
        # Check exam type matches
        if announcement.exam_type:
            exam_type_scores = preference_scores.get("exam_types", {})
            if announcement.exam_type in exam_type_scores and exam_type_scores[announcement.exam_type] > 0:
                reasons.append(f"Similar to your preferred {announcement.exam_type} exams")
        
        # Check location matches
        if announcement.location:
            location_scores = preference_scores.get("locations", {})
            location = announcement.location.get("state") or announcement.location.get("country")
            if location and location in location_scores and location_scores[location] > 0:
                reasons.append(f"Located in your preferred region: {location}")
        
        # Check keyword matches
        if announcement.tags:
            keyword_scores = preference_scores.get("keywords", {})
            matching_keywords = [
                tag for tag in announcement.tags 
                if tag in keyword_scores and keyword_scores[tag] > 0
            ]
            if matching_keywords:
                reasons.append(f"Contains your interested topics: {', '.join(matching_keywords[:3])}")
        
        # Add recency reason
        days_old = (datetime.utcnow() - announcement.created_at).days
        if days_old <= 7:
            reasons.append("Recently published")
        
        return reasons[:3]  # Limit to 3 reasons
    
    async def _find_similar_announcements(
        self, 
        source_announcement: Announcement, 
        limit: int,
        db: Session
    ) -> List[Announcement]:
        """Find announcements similar to the source announcement"""
        
        conditions = []
        
        # Category similarity
        if source_announcement.categories:
            conditions.append(Announcement.categories.op('&&')(source_announcement.categories))
        
        # Exam type similarity
        if source_announcement.exam_type:
            conditions.append(Announcement.exam_type == source_announcement.exam_type)
        
        # Location similarity
        if source_announcement.location:
            location = source_announcement.location.get("state") or source_announcement.location.get("country")
            if location:
                conditions.append(
                    or_(
                        Announcement.location.op('->>')('state') == location,
                        Announcement.location.op('->>')('country') == location
                    )
                )
        
        # Get similar announcements
        query = db.query(Announcement).filter(
            and_(
                Announcement.id != source_announcement.id,
                or_(*conditions) if conditions else True
            )
        )
        
        similar_announcements = query.order_by(desc(Announcement.created_at)).limit(limit).all()
        
        return similar_announcements
    
    async def _find_similar_users(
        self, 
        user_id: str, 
        db: Session
    ) -> List[Tuple[str, float]]:
        """Find users similar to the given user"""
        
        # Get current user profile
        current_profile = await self._get_user_profile(user_id, db)
        current_preferences = current_profile.get("preference_scores", {})
        
        # Get all other users
        other_users = db.query(User).filter(User.id != user_id).all()
        
        similar_users = []
        
        for user in other_users:
            if not user.preferences:
                continue
            
            user_preferences = user.preferences.get("preference_scores", {})
            similarity = self._calculate_user_similarity(current_preferences, user_preferences)
            
            if similarity > 0.3:  # Threshold for similarity
                similar_users.append((str(user.id), similarity))
        
        # Sort by similarity
        similar_users.sort(key=lambda x: x[1], reverse=True)
        
        return similar_users[:10]  # Return top 10 similar users
    
    def _calculate_user_similarity(
        self, 
        preferences1: Dict[str, Any], 
        preferences2: Dict[str, Any]
    ) -> float:
        """Calculate similarity between two user preference profiles"""
        
        total_similarity = 0.0
        weight_sum = 0.0
        
        # Category similarity
        categories1 = preferences1.get("categories", {})
        categories2 = preferences2.get("categories", {})
        if categories1 and categories2:
            category_sim = self._calculate_dict_similarity(categories1, categories2)
            total_similarity += category_sim * 0.4
            weight_sum += 0.4
        
        # Exam type similarity
        exam_types1 = preferences1.get("exam_types", {})
        exam_types2 = preferences2.get("exam_types", {})
        if exam_types1 and exam_types2:
            exam_type_sim = self._calculate_dict_similarity(exam_types1, exam_types2)
            total_similarity += exam_type_sim * 0.3
            weight_sum += 0.3
        
        # Location similarity
        locations1 = preferences1.get("locations", {})
        locations2 = preferences2.get("locations", {})
        if locations1 and locations2:
            location_sim = self._calculate_dict_similarity(locations1, locations2)
            total_similarity += location_sim * 0.2
            weight_sum += 0.2
        
        # Keyword similarity
        keywords1 = preferences1.get("keywords", {})
        keywords2 = preferences2.get("keywords", {})
        if keywords1 and keywords2:
            keyword_sim = self._calculate_dict_similarity(keywords1, keywords2)
            total_similarity += keyword_sim * 0.1
            weight_sum += 0.1
        
        return total_similarity / weight_sum if weight_sum > 0 else 0.0
    
    def _calculate_dict_similarity(self, dict1: Dict[str, float], dict2: Dict[str, float]) -> float:
        """Calculate cosine similarity between two dictionaries"""
        
        # Get all keys
        all_keys = set(dict1.keys()) | set(dict2.keys())
        
        if not all_keys:
            return 0.0
        
        # Create vectors
        vector1 = [dict1.get(key, 0) for key in all_keys]
        vector2 = [dict2.get(key, 0) for key in all_keys]
        
        # Calculate cosine similarity
        dot_product = sum(a * b for a, b in zip(vector1, vector2))
        magnitude1 = math.sqrt(sum(a * a for a in vector1))
        magnitude2 = math.sqrt(sum(b * b for b in vector2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    async def _get_recommendations_from_similar_users(
        self, 
        user_id: str, 
        similar_users: List[Tuple[str, float]], 
        limit: int,
        db: Session
    ) -> List[Dict[str, Any]]:
        """Get recommendations based on similar users' preferences"""
        
        # Get announcements liked by similar users
        similar_user_ids = [user_id for user_id, _ in similar_users]
        
        # This would require tracking user interactions
        # For now, return empty list as this requires more complex implementation
        return []
    
    async def _save_user_profile(self, user_id: str, profile: Dict[str, Any], db: Session):
        """Save user profile to database"""
        
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user.preferences = profile
                db.commit()
                
                # Update cache
                self.user_profiles[user_id] = profile
                
                logger.info("User profile saved", user_id=user_id)
            
        except Exception as e:
            logger.error(f"Failed to save user profile: {e}")
            db.rollback()
            raise


# Global personalization service instance
personalization_service = PersonalizationService()
