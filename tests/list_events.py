import sys
import os
import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

import tools
import config

def list_calendar_events():
    service = tools._get_calendar_service()
    cal_id = config.GOOGLE_CALENDAR_ID.strip()
    
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print(f"[*] Listing events from {now} onwards...")
    
    events_result = service.events().list(
        calendarId=cal_id, 
        timeMin=now,
        maxResults=10, 
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(f"\n- {start} | {event['summary']}")
        print(f"  Description: {event.get('description', 'NO DESCRIPTION')}")
        print(f"  Meet Link: {event.get('hangoutLink', 'NO LINK')}")

if __name__ == "__main__":
    list_calendar_events()
