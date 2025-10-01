#!/usr/bin/env python3
"""Test date extraction from activity descriptions."""

from calendar_scraper import CalendarScraper

cs = CalendarScraper()

test_cases = [
    'select groups by Oct 10',
    'submit by 15-10-2025',
    'deadline: 2025-10-20',
    'Due: Monday, 25 November 2025',
    'before 30th December 2025',
    'Opened: 01-10-2025 Due: 19-10-2025',
    'TMA1 submission drop box Opened:Wednesday, 1 October 2025, 3:07 PMDue:Sunday, 19 October 2025, 11:59 PM'
]

print("Testing date extraction patterns:")
print("=" * 80)

for text in test_cases:
    dates = cs.extract_dates_from_text(text)
    print(f"\nText: {text[:70]}")
    if dates:
        print(f"✓ Found {len(dates)} date(s):")
        for date in dates:
            print(f"  - {date.strftime('%Y-%m-%d')}")
    else:
        print("✗ No dates found")

print("\n" + "=" * 80)
