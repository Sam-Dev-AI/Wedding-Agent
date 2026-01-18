import sys
import os
import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

import tools
import chatbot

def run_booking_test():
    print("\n" + "="*50)
    print("   TEST: AI BOOKING LOGIC & CALENDAR")
    print("="*50)

    # Test 1: Finding a free slot
    print("[*] STEP 1: Checking availability for tomorrow...")
    tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    avail = tools.get_available_slots(tomorrow)
    
    if avail['status'] == 'available':
        slot = avail['slots'][0]
        print(f"[OK] Found available slot: {slot}")
        
        # Test 2: Booking that slot
        print(f"[*] STEP 2: Attempting to book {slot} for tomorrow...")
        res = tools.book_manager_meeting("Test Booker", "samir.lade6@gmail.com", tomorrow, slot)
        
        if res['status'] == 'success':
            print(f"[OK] {res['message']}")
            print("\n[SUCCESS] Booking logic and Calendar sync are working!")
        else:
            print(f"[FAILED] {res['message']}")
    else:
        print(f"[ERROR] No slots available to test booking: {avail.get('message')}")
    
    print("="*50 + "\n")

if __name__ == "__main__":
    run_booking_test()
