import sys
import os
import datetime

# Add/Fix backend path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

import tools
import notifications
import config

def run_final_tests():
    print("\n" + "🚀" + "="*60 + "🚀")
    print("   GRAND OAK ESTATES - COMPREHENSIVE SYSTEM TEST")
    print("="*62 + "\n")

    # 1. KNOWLEDGE (RAG) TEST
    print("[1/4] Testing Knowledge Search (RAG)...")
    try:
        res = tools.search_venue_knowledge("How many guests can the venue hold?")
        if res and len(res) > 20:
             print(f"  [OK] RAG Result Found: {res[:100]}...")
        else:
             print(f"  [FAILED] RAG returned unexpected results: {res}")
    except Exception as e:
        print(f"  [ERROR] RAG Test Error: {e}")

    # 2. EMAIL NOTIFICATION TEST
    print("\n[2/4] Testing Email Delivery...")
    email_success = notifications.send_booking_email(
        client_email=config.SMTP_EMAIL, # Sending to self for verification
        client_name="System Tester",
        booking_type="Final Verification",
        date="2026-01-12",
        time="4:00 PM",
        meet_link="https://meet.google.com/test",
        password="HELL00"
    )
    if email_success:
        print("  [OK] Email system confirmed.")
    else:
        print("  [FAILED] Email delivery failed. Check credentials.")

    # 3. PRECISION AVAILABILITY TEST
    print("\n[3/4] Testing Precision Availability (Whitelisted Model)...")
    tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    avail = tools.get_available_slots(tomorrow)
    if avail['status'] == 'available':
        print(f"  [OK] Found slots tomorrow: {avail['slots']}")
    else:
        print(f"  [NOTE] {avail['message']} (Ensure you have 'Available For Meeting' blocks set on {tomorrow})")

    # 4. CALENDAR SYNC & EARLY START TEST
    print("\n[4/4] Testing Booking Logic & Early Start...")
    if avail['status'] == 'available':
        slot = avail['slots'][0]
        res = tools.book_manager_meeting("Tester", config.SMTP_EMAIL, tomorrow, slot)
        if res['status'] == 'success':
            print(f"  [OK] Meeting booked at {slot}. Message: {res['message']}")
            print(f"  [*] VERIFICATION: Calendar event should start 10 min early (e.g. if 2:00 PM, Cal shows 1:50 PM).")
        else:
             print(f"  [FAILED] Booking failed: {res['message']}")
    else:
        print("  [SKIP] Skipping booking test due to no availability.")

    print("\n" + "="*62)
    print("   TESTING COMPLETE. CHECK YOUR EMAIL AND CALENDAR!")
    print("="*62 + "\n")

if __name__ == "__main__":
    run_final_tests()
