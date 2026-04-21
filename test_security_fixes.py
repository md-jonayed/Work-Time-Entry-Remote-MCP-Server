#!/usr/bin/env python3
"""Quick test to verify critical security fixes"""
import asyncio
from db import register_user, user_exists
from services import add_entry, get_time_entry, update_time_entry, set_schedule, month_summary
from datetime import datetime


async def test_user_isolation():
    """Test that users cannot access other users' data"""
    print("\n" + "="*60)
    print("SECURITY TEST: User Data Isolation")
    print("="*60)

    # Register users
    await register_user("user1@test.com")
    await register_user("user2@test.com")
    print("✓ Users registered")

    # Set schedules
    await set_schedule("user1@test.com", "Monday", 8.0)
    await set_schedule("user2@test.com", "Monday", 9.0)
    print("✓ Different schedules set")

    # Add entries
    today = datetime.now().strftime("%Y-%m-%d")
    entry1 = await add_entry("user1@test.com", today, "09:00", "17:00", "User 1 work")
    entry2 = await add_entry("user2@test.com", today, "08:00", "17:00", "User 2 work")
    print(f"✓ Entries created: ID1={entry1['id']}, ID2={entry2['id']}")

    # TEST 1: User1 cannot read User2's entry
    result = await get_time_entry("user1@test.com", entry2['id'])
    assert "error" in result, "SECURITY FLAW: User1 read User2 entry!"
    print(f"✓ User1 cannot read User2 entry")

    # TEST 2: User1 cannot update User2's entry
    result = await update_time_entry("user1@test.com", entry2['id'], remark="hacked")
    assert "error" in result, "SECURITY FLAW: User1 updated User2 entry!"
    print(f"✓ User1 cannot update User2 entry")

    # TEST 3: User1 can read their own entry
    result = await get_time_entry("user1@test.com", entry1['id'])
    assert "error" not in result, "Failed: User1 cannot read own entry"
    print(f"✓ User1 can read own entry")

    # TEST 4: User1 can update their own entry
    result = await update_time_entry("user1@test.com", entry1['id'], remark="updated")
    assert "error" not in result, "Failed: User1 cannot update own entry"
    assert result['remark'] == "updated", "Failed: Update didn't save correctly"
    print(f"✓ User1 can update own entry")

    # TEST 5: Each user sees only their own data in month summary
    summary1 = await month_summary("user1@test.com", datetime.now().month, datetime.now().year)
    summary2 = await month_summary("user2@test.com", datetime.now().month, datetime.now().year)
    assert summary1['user_id'] == "user1@test.com", "Summary has wrong user_id"
    assert summary2['user_id'] == "user2@test.com", "Summary has wrong user_id"
    # Verify each user only sees their own entries
    assert len(
        summary1['entries']) == 1, f"User1 should see 1 entry, sees {len(summary1['entries'])}"
    assert len(
        summary2['entries']) == 1, f"User2 should see 1 entry, sees {len(summary2['entries'])}"
    # The entries should have different hours based on different work schedules
    assert summary1['entries'][0][
        'hours'] == 8.0, f"User1 entry should be 8 hours, got {summary1['entries'][0]['hours']}"
    assert summary2['entries'][0][
        'hours'] == 9.0, f"User2 entry should be 9 hours, got {summary2['entries'][0]['hours']}"
    print(f"✓ Each user sees only own data in summaries")

    print("\n✓ ALL SECURITY TESTS PASSED!")
    print("✓ User data isolation is properly enforced")
    return True


if __name__ == "__main__":
    try:
        success = asyncio.run(test_user_isolation())
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        exit(1)
