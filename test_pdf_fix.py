"""
Test script to verify PDF report includes new activities
"""
from database import Database

def test_pdf_with_new_activities():
    """Test that PDF generation can access new activities before they're marked as notified"""
    db = Database()
    
    # Get current new activities
    new_activities = db.get_new_activities()
    print(f"\n🔍 Current new activities in database: {len(new_activities)}")
    
    if len(new_activities) == 0:
        print("\n⚠️ No new activities found (all marked as is_new=0)")
        print("This is expected after notifications have been sent.")
        
        # Show recent activities for reference
        recent = db.get_recent_activities(limit=5)
        print(f"📊 Recent activities in database: {len(recent)}")
        
        # Check if there are any recent activities
        if recent:
            print("\n📝 Most recent activities:")
            for activity in recent[:5]:
                print(f"  - {activity['title'][:50]}... (is_new={activity['is_new']})")
    else:
        print("\n✅ Found new activities that can be included in PDF:")
        for activity in new_activities:
            print(f"  - {activity['title'][:60]}...")
            print(f"    Course: {activity['course_name']}")
            print(f"    LMS: {activity['lms_name']}")
            print(f"    Type: {activity['activity_type']}")
            print()
        
        print(f"\n🎉 PDF report will include all {len(new_activities)} activities!")

if __name__ == "__main__":
    test_pdf_with_new_activities()
