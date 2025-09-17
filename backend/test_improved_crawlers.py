#!/usr/bin/env python3
"""
Test script for improved crawlers
"""

from app.crawlers.crawler_manager import crawler_manager

def main():
    print("Testing improved crawlers...")
    
    # Test all crawlers
    result = crawler_manager.run_all_crawlers()
    
    print(f"\n=== Crawl Results ===")
    print(f"Success: {result['success']}")
    print(f"Total announcements saved: {result['total_announcements_saved']}")
    print(f"Successful crawls: {result['successful_crawls']}")
    print(f"Failed crawls: {result['failed_crawls']}")
    print(f"Duration: {result['duration_seconds']:.2f} seconds")
    
    print(f"\n=== Individual Results ===")
    for crawl_result in result['results']:
        print(f"- {crawl_result['source']}: {'✓' if crawl_result['success'] else '✗'} "
              f"({crawl_result.get('saved_count', 0)} saved)")
        if not crawl_result['success']:
            print(f"  Error: {crawl_result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()
