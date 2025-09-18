"""
AI Service for content processing and analysis
"""

import json
import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import structlog
from openai import OpenAI
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.core.config import settings

logger = structlog.get_logger()


class AIService:
    """AI service for content processing and analysis"""
    
    def __init__(self):
        self.openai_client = None
        self.sentence_transformer = None
        self.tfidf_vectorizer = None
        
        # Initialize OpenAI client if API key is available
        if settings.OPENAI_API_KEY:
            try:
                self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
                logger.info("OpenAI client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
        
        # Initialize sentence transformer for semantic similarity
        try:
            self.sentence_transformer = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Sentence transformer initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize sentence transformer: {e}")
        
        # Initialize TF-IDF vectorizer
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
    
    async def extract_structured_data(self, content: str, title: str = "") -> Dict[str, Any]:
        """Extract structured data from announcement content using OpenAI"""
        
        if not self.openai_client or not settings.AI_PROCESSING_ENABLED:
            logger.warning("OpenAI client not available, using fallback extraction")
            return self._fallback_extraction(content, title)
        
        try:
            prompt = self._create_extraction_prompt(content, title)
            
            response = self.openai_client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert at extracting structured information from exam announcements and notifications."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=settings.OPENAI_MAX_TOKENS,
                temperature=settings.OPENAI_TEMPERATURE,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Validate and clean the extracted data
            validated_result = self._validate_extracted_data(result)
            
            logger.info("Successfully extracted structured data using OpenAI")
            return validated_result
            
        except Exception as e:
            logger.error(f"OpenAI extraction failed: {e}")
            return self._fallback_extraction(content, title)
    
    def _create_extraction_prompt(self, content: str, title: str) -> str:
        """Create a structured prompt for data extraction"""
        
        prompt = f"""
        Extract structured information from the following exam announcement:

        Title: {title}
        Content: {content}

        Please extract the following information and return it as a JSON object:

        {{
            "exam_dates": [
                {{
                    "type": "exam type (e.g., 'preliminary', 'main', 'interview')",
                    "start": "exam date in ISO format (YYYY-MM-DDTHH:MM:SSZ)",
                    "end": "exam end date if applicable",
                    "note": "additional notes about the exam"
                }}
            ],
            "application_deadline": "application deadline in ISO format",
            "eligibility": "detailed eligibility criteria",
            "location": {{
                "country": "country name",
                "state": "state/province if applicable",
                "city": "city if applicable"
            }},
            "categories": ["list of relevant exam categories"],
            "tags": ["list of relevant tags"],
            "exam_type": "type of exam (e.g., 'government', 'banking', 'engineering')",
            "difficulty_level": "difficulty level (e.g., 'easy', 'medium', 'hard')",
            "priority_score": "priority score from 1-10 based on importance",
            "confidence": {{
                "dates": "confidence in date extraction (0-1)",
                "eligibility": "confidence in eligibility extraction (0-1)",
                "overall": "overall confidence score (0-1)"
            }}
        }}

        Rules:
        1. Only extract information that is explicitly mentioned in the content
        2. Use null for missing information
        3. Dates should be in ISO format (YYYY-MM-DDTHH:MM:SSZ)
        4. Categories should be relevant exam categories (e.g., 'upsc', 'ssc', 'banking')
        5. Priority score should be based on exam importance and urgency
        6. Confidence scores should reflect how certain you are about the extracted information
        """
        
        return prompt
    
    def _validate_extracted_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean extracted data"""
        
        validated = {
            "exam_dates": [],
            "application_deadline": None,
            "eligibility": None,
            "location": {"country": "India"},
            "categories": [],
            "tags": [],
            "exam_type": "government",
            "difficulty_level": "medium",
            "priority_score": 5.0,
            "confidence": {"dates": 0.5, "eligibility": 0.5, "overall": 0.5}
        }
        
        # Validate exam dates
        if isinstance(data.get("exam_dates"), list):
            for exam_date in data["exam_dates"]:
                if isinstance(exam_date, dict):
                    validated_date = {
                        "type": exam_date.get("type", "exam"),
                        "start": exam_date.get("start"),
                        "end": exam_date.get("end"),
                        "note": exam_date.get("note", "")
                    }
                    if validated_date["start"]:
                        validated["exam_dates"].append(validated_date)
        
        # Validate application deadline
        if data.get("application_deadline"):
            validated["application_deadline"] = data["application_deadline"]
        
        # Validate eligibility
        if data.get("eligibility"):
            validated["eligibility"] = data["eligibility"]
        
        # Validate location
        if isinstance(data.get("location"), dict):
            validated["location"].update(data["location"])
        
        # Validate categories
        if isinstance(data.get("categories"), list):
            validated["categories"] = data["categories"][:5]  # Limit to 5 categories
        
        # Validate tags
        if isinstance(data.get("tags"), list):
            validated["tags"] = data["tags"][:10]  # Limit to 10 tags
        
        # Validate exam type
        if data.get("exam_type"):
            validated["exam_type"] = data["exam_type"]
        
        # Validate difficulty level
        if data.get("difficulty_level"):
            validated["difficulty_level"] = data["difficulty_level"]
        
        # Validate priority score
        if isinstance(data.get("priority_score"), (int, float)):
            validated["priority_score"] = min(max(data["priority_score"], 1), 10)
        
        # Validate confidence
        if isinstance(data.get("confidence"), dict):
            for key in ["dates", "eligibility", "overall"]:
                if key in data["confidence"]:
                    score = data["confidence"][key]
                    if isinstance(score, (int, float)):
                        validated["confidence"][key] = min(max(score, 0), 1)
        
        return validated
    
    def _fallback_extraction(self, content: str, title: str) -> Dict[str, Any]:
        """Fallback extraction using rule-based methods"""
        
        logger.info("Using fallback extraction method")
        
        # Extract dates using regex
        exam_dates = self._extract_dates_fallback(content)
        
        # Extract eligibility using keywords
        eligibility = self._extract_eligibility_fallback(content)
        
        # Extract categories from title and content
        categories = self._extract_categories_fallback(title, content)
        
        # Calculate priority score
        priority_score = self._calculate_priority_score_fallback(title, content)
        
        return {
            "exam_dates": exam_dates,
            "application_deadline": None,
            "eligibility": eligibility,
            "location": {"country": "India"},
            "categories": categories,
            "tags": categories[:5],
            "exam_type": "government",
            "difficulty_level": "medium",
            "priority_score": priority_score,
            "confidence": {"dates": 0.3, "eligibility": 0.4, "overall": 0.35}
        }
    
    def _extract_dates_fallback(self, content: str) -> List[Dict[str, str]]:
        """Extract dates using regex patterns"""
        
        dates = []
        
        # Common date patterns
        date_patterns = [
            r'(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
            r'(\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{2,4})',
            r'(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{2,4})'
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                dates.append({
                    "type": "exam",
                    "start": match,
                    "end": None,
                    "note": "Extracted using regex"
                })
        
        return dates[:3]  # Limit to 3 dates
    
    def _extract_eligibility_fallback(self, content: str) -> Optional[str]:
        """Extract eligibility criteria using keywords"""
        
        eligibility_keywords = [
            "eligibility", "qualification", "educational qualification",
            "age limit", "age criteria", "minimum age", "maximum age",
            "degree", "graduation", "post graduation", "diploma"
        ]
        
        sentences = content.split('.')
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in eligibility_keywords):
                return sentence.strip()
        
        return None
    
    def _extract_categories_fallback(self, title: str, content: str) -> List[str]:
        """Extract categories using keyword matching"""
        
        categories = []
        text = f"{title} {content}".lower()
        
        # Exam category keywords
        category_keywords = {
            "upsc": ["upsc", "union public service commission", "civil services"],
            "ssc": ["ssc", "staff selection commission", "cgl", "chsl"],
            "banking": ["banking", "ibps", "sbi", "po", "clerk"],
            "engineering": ["engineering", "gate", "jee", "neet"],
            "railway": ["railway", "rrb", "ntpc", "group d"],
            "defense": ["army", "navy", "air force", "defense", "military"],
            "teaching": ["teaching", "teacher", "education", "tet", "ctet"],
            "police": ["police", "constable", "si", "inspector"]
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in text for keyword in keywords):
                categories.append(category)
        
        return categories[:5]  # Limit to 5 categories
    
    def _calculate_priority_score_fallback(self, title: str, content: str) -> float:
        """Calculate priority score using keyword analysis"""
        
        text = f"{title} {content}".lower()
        score = 5.0  # Base score
        
        # High priority keywords
        high_priority = ["urgent", "important", "deadline", "last date", "notification"]
        for keyword in high_priority:
            if keyword in text:
                score += 1.0
        
        # Medium priority keywords
        medium_priority = ["recruitment", "examination", "admission", "application"]
        for keyword in medium_priority:
            if keyword in text:
                score += 0.5
        
        # Exam type priority
        if "upsc" in text:
            score += 2.0
        elif "ssc" in text:
            score += 1.5
        elif "banking" in text or "ibps" in text:
            score += 1.0
        
        return min(max(score, 1.0), 10.0)
    
    def calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between two texts"""
        
        if not self.sentence_transformer:
            # Fallback to TF-IDF similarity
            return self._calculate_tfidf_similarity(text1, text2)
        
        try:
            # Get embeddings
            embeddings = self.sentence_transformer.encode([text1, text2])
            
            # Calculate cosine similarity
            similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Semantic similarity calculation failed: {e}")
            return self._calculate_tfidf_similarity(text1, text2)
    
    def _calculate_tfidf_similarity(self, text1: str, text2: str) -> float:
        """Calculate TF-IDF similarity as fallback"""
        
        try:
            tfidf_matrix = self.tfidf_vectorizer.fit_transform([text1, text2])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return float(similarity)
        except Exception as e:
            logger.error(f"TF-IDF similarity calculation failed: {e}")
            return 0.0
    
    def detect_duplicates(self, announcements: List[Dict[str, Any]], threshold: float = 0.8) -> List[Tuple[int, int, float]]:
        """Detect duplicate announcements based on semantic similarity"""
        
        duplicates = []
        
        for i in range(len(announcements)):
            for j in range(i + 1, len(announcements)):
                text1 = f"{announcements[i].get('title', '')} {announcements[i].get('summary', '')}"
                text2 = f"{announcements[j].get('title', '')} {announcements[j].get('summary', '')}"
                
                similarity = self.calculate_semantic_similarity(text1, text2)
                
                if similarity >= threshold:
                    duplicates.append((i, j, similarity))
        
        return duplicates
    
    def generate_summary(self, content: str, max_length: int = 150) -> str:
        """Generate a summary of the content"""
        
        if not self.openai_client or not settings.AI_PROCESSING_ENABLED:
            return self._fallback_summary(content, max_length)
        
        try:
            prompt = f"""
            Summarize the following exam announcement in {max_length} characters or less:
            
            {content}
            
            The summary should be clear, concise, and highlight the key information like exam name, important dates, and eligibility criteria.
            """
            
            response = self.openai_client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert at summarizing exam announcements concisely."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.3
            )
            
            summary = response.choices[0].message.content.strip()
            return summary[:max_length]
            
        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            return self._fallback_summary(content, max_length)
    
    def _fallback_summary(self, content: str, max_length: int) -> str:
        """Generate summary using simple text extraction"""
        
        # Extract first sentence or first 150 characters
        sentences = content.split('.')
        if sentences:
            first_sentence = sentences[0].strip()
            if len(first_sentence) <= max_length:
                return first_sentence
        
        # Truncate content
        return content[:max_length].strip() + "..." if len(content) > max_length else content


# Global AI service instance
ai_service = AIService()
