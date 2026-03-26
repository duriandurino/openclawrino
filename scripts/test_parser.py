#!/usr/bin/env python3
"""
Pentest Report Parser Test
Tests markdown parsing without Google API authentication.
"""

import sys
sys.path.insert(0, '/home/dukali/.openclaw/workspace/scripts')

from pentest_slides_generator import PentestSlidesGenerator

def test_parser():
    """Test the markdown parser on the vault report."""
    
    # Read the report
    with open('/home/dukali/.openclaw/workspace/engagements/player-vault/reporting/REPORT_SLIDES.md', 'r') as f:
        content = f.read()
    
    # Create generator (without auth for testing)
    generator = PentestSlidesGenerator.__new__(PentestSlidesGenerator)
    
    # Parse the markdown
    slides = generator.parse_markdown(content)
    
    print(f"✅ Successfully parsed {len(slides)} slides\n")
    print("=" * 60)
    
    for i, slide in enumerate(slides[:10], 1):  # Show first 10
        print(f"\n📊 SLIDE {i}: {slide.get('title', 'Untitled')}")
        print(f"   Type: {slide.get('type', 'content')}")
        print(f"   Content items: {len(slide.get('content', []))}")
        
        for item in slide.get('content', [])[:5]:  # Show first 5 items
            item_type = item.get('type', 'text')
            if item_type == 'table':
                print(f"   📋 Table: {len(item['data']['headers'])} cols x {len(item['data']['rows'])} rows")
            elif item_type == 'severity':
                print(f"   🔴 {item['severity']}: {item['text'][:50]}...")
            elif item_type == 'bullet':
                print(f"   • {item['text'][:50]}...")
            else:
                print(f"   📝 {item['text'][:50]}...")
        
        if len(slide.get('content', [])) > 5:
            print(f"   ... and {len(slide['content']) - 5} more items")
    
    print("\n" + "=" * 60)
    print(f"\n✅ Parser test complete! {len(slides)} slides ready for Google Slides API")
    
    return slides

if __name__ == '__main__':
    test_parser()
