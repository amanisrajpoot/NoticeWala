"""
AI-powered extraction service for announcements
"""

import json
from typing import Dict, Any, Optional, List
import structlog
from openai import OpenAI

from app.core.config import settings

logger = structlog.get_logger()


class ExtractionService:
    """Service for extracting structured data from raw content"""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
        self.extraction_prompt = self._get_extraction_prompt()
    
    def _get_extraction_prompt(self) -> str:
        """Get the extraction prompt template"""
        return """
You are a precise data extractor for exam and educational notifications. 
Extract structured information from the provided content and return ONLY valid JSON.

Input: Raw HTML/text content of an exam notification
Output: JSON object with the following structure:

{
  "title": "string - Main title of the announcement",
  "summary": "string - 25-40 word summary",
  "publish_date": "ISO date string or null",
  "exam_dates": [
    {
      "type": "exam_date|application_deadline|result_date",
      "start": "ISO date string",
      "end": "ISO date string or null",
      "note": "string or null"
    }
  ],
  "application_deadline": "ISO date string or null",
  "eligibility": "string or null - Eligibility criteria",
  "location": {
    "country": "string or null",
    "state": "string or null", 
    "city": "string or null"
  },
  "categories": ["string array - exam categories"],
  "tags": ["string array - relevant tags"],
  "confidence": {
    "title": 0.0-1.0,
    "dates": 0.0-1.0,
    "eligibility": 0.0-1.0
  }
}

Rules:
1. Return ONLY valid JSON, no explanations
2. Use ISO date format (YYYY-MM-DD) for dates
3. If information is missing, use null
4. Categories should be from: school, college, government, competitive, engineering, medical, scholarship, certification
5. Extract dates even if in different formats
6. Be conservative with confidence scores
7. Summary should be concise and informative

Content to extract from:
"""
    
    def extract_from_content(self, content: str, source_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract structured data from content using AI"""
        
        if not self.client:
            logger.warning("OpenAI client not available, using fallback extraction")
            return self._fallback_extraction(content, source_info)
        
        try:
            # Prepare the prompt
            full_prompt = self.extraction_prompt + content
            
            # Make API call
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a precise data extraction assistant. Return only valid JSON."},
                    {"role": "user", "content": full_prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            # Parse response
            extracted_data = json.loads(response.choices[0].message.content)
            
            # Validate and clean the data
            cleaned_data = self._validate_extraction(extracted_data)
            
            logger.info("AI extraction successful", confidence=cleaned_data.get('confidence', {}))
            return cleaned_data
            
        except json.JSONDecodeError as e:
            logger.error("Failed to parse AI extraction JSON", error=str(e))
            return self._fallback_extraction(content, source_info)
        except Exception as e:
            logger.error("AI extraction failed", error=str(e))
            return self._fallback_extraction(content, source_info)
    
    def _fallback_extraction(self, content: str, source_info: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback extraction using simple rules when AI is not available"""
        
        # Basic title extraction
        title = self._extract_title(content)
        
        # Basic date extraction
        dates = self._extract_dates(content)
        
        return {
            "title": title,
            "summary": self._generate_summary(content, title),
            "publish_date": None,
            "exam_dates": dates,
            "application_deadline": None,
            "eligibility": None,
            "location": {
                "country": "IN",
                "state": None,
                "city": None
            },
            "categories": self._extract_categories(content, source_info),
            "tags": self._extract_tags(content),
            "confidence": {
                "title": 0.7,
                "dates": 0.5,
                "eligibility": 0.3
            }
        }
    
    def _extract_title(self, content: str) -> str:
        """Extract title from content"""
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if len(line) > 10 and len(line) < 200:
                return line
        return "Untitled Announcement"
    
    def _extract_dates(self, content: str) -> List[Dict[str, Any]]:
        """Extract dates from content using simple patterns"""
        # This is a simplified version - in production, use dateparser
        import re
        
        date_patterns = [
            r'(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
            r'(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4})',
        ]
        
        dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                dates.append({
                    "type": "exam_date",
                    "start": match,
                    "end": None,
                    "note": None
                })
        
        return dates
    
    def _extract_categories(self, content: str, source_info: Dict[str, Any]) -> List[str]:
        """Extract categories based on content and source"""
        categories = []
        
        content_lower = content.lower()
        
        if any(word in content_lower for word in ['government', 'public', 'civil service']):
            categories.append('government')
        
        if any(word in content_lower for word in ['engineering', 'jee', 'iit', 'nit']):
            categories.append('engineering')
        
        if any(word in content_lower for word in ['medical', 'neet', 'mbbs', 'doctor']):
            categories.append('medical')
        
        if any(word in content_lower for word in ['scholarship', 'fellowship', 'grant']):
            categories.append('scholarship')
        
        # Add source-based category
        source_category = source_info.get('category', 'other')
        if source_category not in categories:
            categories.append(source_category)
        
        return categories if categories else ['other']
    
    def _extract_tags(self, content: str) -> List[str]:
        """Extract relevant tags from content"""
        import re
        
        # Common exam-related keywords
        keywords = [
            'notification', 'application', 'admission', 'entrance', 'exam',
            'result', 'merit list', 'interview', 'counseling', 'registration'
        ]
        
        tags = []
        content_lower = content.lower()
        
        for keyword in keywords:
            if keyword in content_lower:
                tags.append(keyword.replace(' ', '_'))
        
        return tags
    
    def _generate_summary(self, content: str, title: str) -> str:
        """Generate a simple summary"""
        # Take first few words from content or use title
        words = content.split()[:20]
        summary = ' '.join(words)
        
        if len(summary) > 100:
            summary = summary[:97] + "..."
        
        return summary or title
    
    def _validate_extraction(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean extracted data"""
        
        # Ensure required fields exist
        validated = {
            "title": data.get("title", "Untitled Announcement"),
            "summary": data.get("summary", ""),
            "publish_date": data.get("publish_date"),
            "exam_dates": data.get("exam_dates", []),
            "application_deadline": data.get("application_deadline"),
            "eligibility": data.get("eligibility"),
            "location": data.get("location", {}),
            "categories": data.get("categories", []),
            "tags": data.get("tags", []),
            "confidence": data.get("confidence", {})
        }
        
        # Clean and validate title
        if not validated["title"] or len(validated["title"]) < 5:
            validated["title"] = "Untitled Announcement"
        
        # Ensure confidence scores are valid
        confidence = validated["confidence"]
        for key in ["title", "dates", "eligibility"]:
            if key not in confidence:
                confidence[key] = 0.5
            else:
                confidence[key] = max(0.0, min(1.0, confidence[key]))
        
        return validated
