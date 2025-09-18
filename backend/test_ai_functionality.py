#!/usr/bin/env python3
"""
Test script for AI functionality
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.ai_service import ai_service
from app.crawlers.ai_enhanced_crawler import AIEnhancedCrawler
import structlog

logger = structlog.get_logger()


async def test_ai_service():
    """Test AI service functionality"""
    
    print("🤖 Testing AI Service Functionality")
    print("=" * 50)
    
    # Test content
    test_content = """
    Union Public Service Commission (UPSC) has released the notification for Civil Services Examination 2024.
    
    Important Dates:
    - Application Start Date: 14th February 2024
    - Application End Date: 5th March 2024
    - Preliminary Examination: 26th May 2024
    - Main Examination: 20th September 2024
    
    Eligibility Criteria:
    - Age Limit: 21-32 years (relaxations applicable)
    - Educational Qualification: Bachelor's degree from recognized university
    - Nationality: Indian citizen
    
    The examination will be conducted in multiple phases including Preliminary, Main, and Interview.
    """
    
    test_title = "UPSC Civil Services Examination 2024 Notification"
    
    print(f"📝 Testing content extraction...")
    print(f"Title: {test_title}")
    print(f"Content length: {len(test_content)} characters")
    
    try:
        # Test structured data extraction
        print("\n🔍 Testing structured data extraction...")
        result = await ai_service.extract_structured_data(test_content, test_title)
        
        print("✅ Extraction successful!")
        print(f"📊 Results:")
        print(f"  - Exam dates found: {len(result.get('exam_dates', []))}")
        print(f"  - Application deadline: {result.get('application_deadline', 'Not found')}")
        print(f"  - Categories: {result.get('categories', [])}")
        print(f"  - Priority score: {result.get('priority_score', 'N/A')}")
        print(f"  - Overall confidence: {result.get('confidence', {}).get('overall', 'N/A')}")
        
        # Test summary generation
        print("\n📋 Testing summary generation...")
        summary = ai_service.generate_summary(test_content, 100)
        print(f"✅ Summary generated: {summary}")
        
        # Test semantic similarity
        print("\n🔗 Testing semantic similarity...")
        similar_text = "UPSC CSE 2024 notification for civil services examination with important dates and eligibility criteria."
        similarity = ai_service.calculate_semantic_similarity(test_title, similar_text)
        print(f"✅ Similarity score: {similarity:.3f}")
        
        return True
        
    except Exception as e:
        print(f"❌ AI service test failed: {e}")
        return False


def test_ai_enhanced_crawler():
    """Test AI enhanced crawler"""
    
    print("\n🕷️ Testing AI Enhanced Crawler")
    print("=" * 50)
    
    try:
        # Create AI enhanced crawler
        ai_crawler = AIEnhancedCrawler("test_ai_crawler", "https://test.local")
        
        print("✅ AI enhanced crawler created successfully")
        
        # Test source info
        source_info = ai_crawler.get_source_info()
        print(f"📊 Source info: {source_info['name']}")
        
        # Test insights generation
        print("\n📈 Testing insights generation...")
        insights = ai_crawler.generate_insights()
        print(f"✅ Insights generated:")
        print(f"  - Total announcements: {insights.get('total_announcements', 0)}")
        print(f"  - Top categories: {insights.get('top_categories', [])[:3]}")
        print(f"  - Average priority: {insights.get('average_priority_score', 0):.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ AI enhanced crawler test failed: {e}")
        return False


async def test_duplicate_detection():
    """Test duplicate detection functionality"""
    
    print("\n🔍 Testing Duplicate Detection")
    print("=" * 50)
    
    try:
        # Test data
        announcements = [
            {
                "title": "UPSC Civil Services Examination 2024",
                "summary": "Notification for UPSC CSE 2024 with important dates and eligibility criteria.",
                "content": "Union Public Service Commission has released the notification for Civil Services Examination 2024."
            },
            {
                "title": "UPSC CSE 2024 Notification",
                "summary": "Civil Services Examination 2024 notification with dates and requirements.",
                "content": "UPSC has announced the Civil Services Examination 2024 notification with all details."
            },
            {
                "title": "SSC CGL Examination 2024",
                "summary": "Staff Selection Commission CGL 2024 notification.",
                "content": "SSC has released the notification for Combined Graduate Level Examination 2024."
            }
        ]
        
        # Detect duplicates
        duplicates = ai_service.detect_duplicates(announcements, threshold=0.7)
        
        print(f"✅ Duplicate detection completed")
        print(f"📊 Found {len(duplicates)} potential duplicates:")
        
        for i, j, similarity in duplicates:
            print(f"  - Announcements {i} and {j}: {similarity:.3f} similarity")
        
        return True
        
    except Exception as e:
        print(f"❌ Duplicate detection test failed: {e}")
        return False


async def main():
    """Main test function"""
    
    print("🚀 NoticeWala AI Functionality Test")
    print("=" * 60)
    
    # Test AI service
    ai_service_success = await test_ai_service()
    
    # Test AI enhanced crawler
    ai_crawler_success = test_ai_enhanced_crawler()
    
    # Test duplicate detection
    duplicate_success = await test_duplicate_detection()
    
    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 50)
    print(f"🤖 AI Service: {'✅ PASS' if ai_service_success else '❌ FAIL'}")
    print(f"🕷️ AI Enhanced Crawler: {'✅ PASS' if ai_crawler_success else '❌ FAIL'}")
    print(f"🔍 Duplicate Detection: {'✅ PASS' if duplicate_success else '❌ FAIL'}")
    
    total_tests = 3
    passed_tests = sum([ai_service_success, ai_crawler_success, duplicate_success])
    
    print(f"\n🎯 Overall Result: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All AI functionality tests passed!")
        return True
    else:
        print("⚠️ Some tests failed. Check the logs above for details.")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
