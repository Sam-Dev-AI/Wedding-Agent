import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

import notifications
import config

def run_email_test():
    print("\n" + "="*50)
    print("   TEST: EMAIL NOTIFICATION SYSTEM")
    print("="*50)
    
    test_email = "samir.lade6@gmail.com" # Using user's email for verification
    test_name = "Test User"
    
    print(f"[*] Attempting to send test email to: {test_email}")
    
    success = notifications.send_booking_email(
        client_email=test_email,
        client_name=test_name,
        booking_type="Test Meeting",
        date="2026-01-12",
        time="2:00 PM",
        meet_link="https://meet.google.com/test-link"
    )
    
    if success:
        print("\n[SUCCESS] Email sent successfully! Please check your inbox.")
    else:
        print("\n[FAILED] Email delivery failed. Check SMTP credentials in config.py.")
    print("="*50 + "\n")

if __name__ == "__main__":
    run_email_test()
