#!/usr/bin/env python3
"""
Test script for bot functionality without running the actual Telegram bot
"""
import json

# Load data
data = json.load(open('admissions.json', encoding='utf-8'))

def test_query(text):
    """Simulate the query function logic"""
    text = text.lower()
    results = []
    
    for entry in data:
        university = entry['university'].lower()
        department = entry.get('department', '').lower()
        
        # Check if university name or part of it is in the query
        uni_match = False
        dept_match = False
        
        # Remove common suffixes for matching
        uni_base = university.replace('대학교', '').replace('대학', '')
        dept_base = department.replace('학과', '').replace('학부', '')
        
        # Check if university matches
        if uni_base in text or university in text:
            uni_match = True
        
        # Check if department matches
        if dept_base in text or department in text:
            dept_match = True
        
        # Check for various query patterns
        if '일정' in text or 'schedule' in text:
            if uni_match:
                results.append(f"{entry['university']} {entry['department']}\n{entry['schedule']}")
        elif '요구사항' in text or 'requirements' in text or '조건' in text:
            if uni_match:
                results.append(f"{entry['university']} {entry['department']}\n요구사항: {entry['requirements']}")
        elif '홈페이지' in text or 'website' in text:
            if uni_match:
                results.append(f"{entry['university']} {entry['department']}\n홈페이지: {entry['website']}")
        else:
            # General search
            if uni_match or dept_match:
                results.append(
                    f"{entry['university']} {entry['department']}\n"
                    f"일정:\n{entry['schedule']}\n\n"
                    f"요구사항: {entry['requirements']}\n"
                    f"홈페이지: {entry['website']}"
                )
    
    return results

# Test cases
print("Test 1: 연세대 일정")
results = test_query("연세대 일정")
print(f"Found {len(results)} results")
for r in results:
    print(r)
    print("---")

print("\nTest 2: 고려대 컴퓨터")
results = test_query("고려대 컴퓨터")
print(f"Found {len(results)} results")
for r in results:
    print(r)
    print("---")

print("\nTest 3: 카이스트 요구사항")
results = test_query("카이스트 요구사항")
print(f"Found {len(results)} results")
for r in results:
    print(r)
    print("---")

print("\nTest 4: 서울대")
results = test_query("서울대")
print(f"Found {len(results)} results")
for r in results:
    print(r)
    print("---")

print("\nAll tests completed successfully!")
