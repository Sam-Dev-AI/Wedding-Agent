from google.oauth2 import service_account
from googleapiclient.discovery import build
import datetime
from datetime import timedelta
import config
import notifications
import os
import json

# Scopes required for the Calendar API
SCOPES = ['https://www.googleapis.com/auth/calendar']

def _get_calendar_service():
    if not os.path.exists(config.CREDENTIALS_FILE):
        return None
    
    try:
        creds = service_account.Credentials.from_service_account_file(
            config.CREDENTIALS_FILE, scopes=SCOPES)
        return build('calendar', 'v3', credentials=creds)
    except Exception as e:
        print(f"!! Google Auth Error: {e}")
        return None

def _format_date(date_str: str):
    """Helper to ensure date is in YYYY-MM-DD format."""
    # Clean up input (e.g. "12 jan" -> "12 jan 2026" if needed?)
    date_str = date_str.strip()
    
    # Try parsing with year
    formats_with_year = ["%Y-%m-%d", "%B %d, %Y", "%b %d, %Y", "%d %b %Y", "%d %B %Y", "%Y/%m/%d"]
    for fmt in formats_with_year:
        try:
            return datetime.datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
        except:
            continue
            
    # Try parsing without year (assume current year, or next if passed)
    formats_no_year = ["%d %b", "%d %B", "%b %d", "%B %d"]
    current_year = datetime.datetime.now().year
    for fmt in formats_no_year:
        try:
            dt = datetime.datetime.strptime(date_str, fmt)
            # Default to current year
            dt = dt.replace(year=current_year)
            # If date is in past (more than 30 days?), maybe they mean next year? 
            # For simplicity, just use current year as weddings are usually future.
            # If user asks "12 Jan" in Dec 2025, they mean Jan 2026.
            if dt < datetime.datetime.now() - timedelta(days=30):
                 dt = dt.replace(year=current_year + 1)
            return dt.strftime("%Y-%m-%d")
        except:
            continue
            
    return date_str # Return as is if all fail

def check_wedding_hall_availability(date_str: str):
    """Checks if the Wedding Hall is free for a full day. A day is BUSY if an event contains 'hall' or 'booked'."""
    date_str = _format_date(date_str)
    print(f"\n[GOOGLE CAL] Checking Hall: {date_str}")
    service = _get_calendar_service()
    if not service:
        return {"available": False, "message": "Calendar service is not configured."}

    try:
        # Strip any accidental whitespace from the ID
        cal_id = config.GOOGLE_CALENDAR_ID.strip()
        time_min = f"{date_str}T00:00:00{config.UTC_OFFSET}"
        time_max = f"{date_str}T23:59:59{config.UTC_OFFSET}"

        events_result = service.events().list(
            calendarId=cal_id,
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True
        ).execute()
        
        events = events_result.get('items', [])
        
        # SMART FILTER: Only block if title contains "hall" or "booked"
        relevant_events = []
        for e in events:
            summary = e.get('summary', '').lower()
            if not any(k in summary for k in ['hall', 'booked', 'reservation']):
                continue
            
            # Fix: Ignore "All Day" events that are for a different day (due to timezone overlap)
            # If it's an all day event, 'start' has 'date' field (e.g. "2026-01-13")
            start_date = e['start'].get('date')
            if start_date and start_date != date_str:
                continue

            relevant_events.append(e)

        is_reserved = len(relevant_events) > 0
        
        print(f"  <- STATUS: {'BUSY (Keyword Match)' if is_reserved else 'FREE (No Hall Keywords)'}")

        if not is_reserved:
            display_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").strftime("%B %d, %Y")
            return {"available": True, "message": f"I am delighted to share that Grand Oak Estates is available for your celebration on {display_date}."}
        
        # Search for 3 days before and 3 days after
        alternatives = []
        target_dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        for offset in [1, 2, 3, -1, -2, -3]: # Check after first as usually preferred
            check_dt = target_dt + timedelta(days=offset)
            # Skip past dates if any
            if check_dt.date() < datetime.datetime.now().date(): continue
            
            d_str = check_dt.strftime("%Y-%m-%d")
            t_min = f"{d_str}T00:00:00{config.UTC_OFFSET}"
            t_max = f"{d_str}T23:59:59{config.UTC_OFFSET}"
            
            res = service.events().list(calendarId=cal_id, timeMin=t_min, timeMax=t_max, singleEvents=True).execute()
            items = res.get('items', [])
            
            # Apply same smart filters to alternatives
            is_alt_busy = False
            for e in items:
                matches_keyword = any(k in e.get('summary', '').lower() for k in ['hall', 'booked', 'reservation'])
                if matches_keyword:
                    # Check date match for all-day events
                    start_d = e['start'].get('date')
                    if start_d and start_d != d_str:
                        continue
                    is_alt_busy = True
                    break
            
            if not is_alt_busy:
                alternatives.append(check_dt.strftime("%B %d"))
            if len(alternatives) >= 3: break

        alt_text = f" However, I have exquisite availability on {', '.join(alternatives[:-1])} and {alternatives[-1]} if those dates might suit your vision." if alternatives else ""
        return {
            "available": False,
            "message": f"The sanctuary is currently reserved for a private gala on {target_dt.strftime('%B %d')}.{alt_text}"
        }
    except Exception as e:
        error_str = str(e)
        if "404" in error_str:
            cal_id = config.GOOGLE_CALENDAR_ID.strip()
            print(f"  !! ERROR 404: Calendar '{cal_id}' Not Found.")
            print("  !! ACTION: Please ensure you shared the calendar with the SERVICE ACCOUNT email.")
            return {"available": False, "message": "I cannot access the calendar. Please ensure you have shared it with my Service Account email."}
        print(f"  !! Error: {e}")
        return {"available": False, "message": "I encountered a sync issue."}

def get_available_slots(date_str: str):
    """Lists 1-hour gaps for meetings/tours within working hours (10 AM - 7 PM), avoiding conflicts."""
    date_str = _format_date(date_str)
    print(f"\n[GOOGLE CAL] Finding Free Slots (Implicit): {date_str}")
    service = _get_calendar_service()
    if not service: return {"status": "error", "message": "No service."}

    try:
        cal_id = config.GOOGLE_CALENDAR_ID.strip()
        
        # Working Hours: 10:00 AM to 7:00 PM
        work_start_hour = 10
        work_end_hour = 19
        
        import pytz
        tz = pytz.timezone(config.TIMEZONE)
        
        # Define day boundaries in UTC for query
        day_start = datetime.datetime.strptime(date_str, "%Y-%m-%d").replace(hour=0, minute=0, second=0)
        day_end = datetime.datetime.strptime(date_str, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
        
        # Helper to convert local time to ISO string with current offset
        # Note: We rely on the calendar usage's timezone, simplified here by string manipulation or proper localization
        # To avoid complex TZ issues, we'll fetch ensuring singleEvents=True handles expanding
        
        time_min = f"{date_str}T00:00:00{config.UTC_OFFSET}"
        time_max = f"{date_str}T23:59:59{config.UTC_OFFSET}"
        
        # Fetch ALL events for the day
        events_result = service.events().list(
            calendarId=cal_id,
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        day_events = events_result.get('items', [])

        busy_intervals = []
        explicit_availability_windows = []
        
        avail_keywords = ['available', 'free', 'open']
        ignore_keywords = ['hall reserved', 'wedding']
        
        for e in day_events:
            if e.get('transparency') == 'transparent': continue
            
            summary = e.get('summary', '').lower()
            start_raw = e['start'].get('dateTime') or e['start'].get('date')
            end_raw = e['end'].get('dateTime') or e['end'].get('date')
            
            # Normalize to datetime (naïve for simplicity in this script, assuming local calls)
            if 'T' in start_raw:
                s_dt = datetime.datetime.fromisoformat(start_raw).replace(tzinfo=None)
                e_dt = datetime.datetime.fromisoformat(end_raw).replace(tzinfo=None)
            else:
                s_dt = datetime.datetime.strptime(start_raw, "%Y-%m-%d")
                e_dt = datetime.datetime.strptime(end_raw, "%Y-%m-%d") + timedelta(days=1)

            # Classify Event
            is_explicit = any(k in summary for k in avail_keywords)
            is_ignored = any(k in summary for k in ignore_keywords)
            
            if is_explicit:
                explicit_availability_windows.append((s_dt, e_dt))
            elif is_ignored:
                pass 
            else:
                busy_intervals.append((s_dt, e_dt))

        # Generate Candidate Slots
        valid_slots = []
        base_day = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        
        curr_hour = work_start_hour
        curr_minute = 0
        
        while True:
            # Construct candidate slot start/end (Naïve)
            slot_start = base_day.replace(hour=curr_hour, minute=curr_minute)
            slot_end = slot_start + timedelta(hours=1)
            
            # Stop if the slot ends after working hours
            if slot_end.hour > work_end_hour or (slot_end.hour == work_end_hour and slot_end.minute > 0):
                break
            
            # CHECK 1: Explicit Window Constraint
            # If explicit windows exist, slot must be inside at least one.
            allowed_by_explicit = False
            if not explicit_availability_windows:
                allowed_by_explicit = True # Implicit Mode
            else:
                for w_start, w_end in explicit_availability_windows:
                    # Slot inside window? start >= w_start AND end <= w_end
                    if slot_start >= w_start and slot_end <= w_end:
                        allowed_by_explicit = True
                        break
            
            # CHECK 2: Busy Interval Constraint
            is_busy = False
            for b_start, b_end in busy_intervals:
                # Overlap check
                if not (slot_end <= b_start or slot_start >= b_end):
                    is_busy = True
                    break
            
            if allowed_by_explicit and not is_busy:
                # Check Past (Same as before)
                now_naive = datetime.datetime.now(tz).replace(tzinfo=None)
                today_naive = datetime.datetime.now(tz).date()
                if not (base_day.date() == today_naive and slot_start < now_naive):
                    valid_slots.append(slot_start.strftime("%I:%M %p"))
                else: 
                     is_busy = True # Mark as busy for logic cleanliness if debugging
            else:
                is_busy = True # Implicitly busy if not allowed
            
            # Increment by 30 mins (Logic handled above)
            
            # Increment by 30 mins
            if curr_minute == 0:
                curr_minute = 30
            else:
                curr_minute = 0
                curr_hour += 1
                
        print(f"  <- FOUND SLOTS: {len(valid_slots)}")
        if not valid_slots:
            return {"status": "busy", "message": "I am afraid fully booked for tours on that date. May I suggest checking the following day?"}
        
        # LOGIC: Group contiguous slots into ranges
        # slots are strings "10:00 AM". Convert to minutes for logic.
        def to_mins(t_str):
            t = datetime.datetime.strptime(t_str, "%I:%M %p")
            return t.hour * 60 + t.minute
            
        if len(valid_slots) > 3:
            ranges = []
            current_range = [valid_slots[0]]
            
            for i in range(1, len(valid_slots)):
                prev_mins = to_mins(current_range[-1])
                curr_mins = to_mins(valid_slots[i])
                
                # Check if contiguous (30 min gap)
                if curr_mins - prev_mins == 30:
                    current_range.append(valid_slots[i])
                else:
                    ranges.append(current_range)
                    current_range = [valid_slots[i]]
            ranges.append(current_range)
            
            # Format ranges
            readable_parts = []
            for r in ranges:
                if len(r) >= 3:
                    # It's a range. Start Time -> Last Time + 30 mins (approx 1 hr block? No, "free from X to Y")
                    # If slots are 10:00, 10:30, 11:00. This covers 10:00 AM to 12:00 PM (11 + 1hr).
                    # Actually simpler: "I am free between [Start] and [End + 1hr]"? 
                    # User asked: "free on 12pm to 3pm".
                    # Let's say range start is r[0]. Range end is r[-1] + 1 hour (since slots are 1h blocks).
                    
                    t_start = r[0]
                    t_last = datetime.datetime.strptime(r[-1], "%I:%M %p")
                    t_end_dt = t_last + timedelta(hours=1)
                    t_end = t_end_dt.strftime("%I:%M %p").lstrip('0') # Remove leading zero
                    t_start_nice = t_start.lstrip('0')
                    
                    readable_parts.append(f"{t_start_nice} to {t_end}")
                else:
                    # List individual
                    readable_parts.extend([t.lstrip('0') for t in r])
            
            msg_slots = ", ".join(readable_parts[:-1]) + " and " + readable_parts[-1] if len(readable_parts) > 1 else readable_parts[0]
            display_msg = f"I have wide availability on that date, specifically {msg_slots}."
        else:
            # Fallback for few slots
            display_msg = f"I have the following tour times available: {', '.join(valid_slots)}."

        return {"status": "available", "slots": valid_slots, "message": display_msg}

    except Exception as e:
        print(f"ERROR: {e}")
        return {"status": "error", "message": str(e)}

def _create_event(name, email, date_str, time_str, summary_template):
    date_str = _format_date(date_str)
    service = _get_calendar_service()
    if not service: return {"status": "error", "message": "No service."}

    try:
        cal_id = config.GOOGLE_CALENDAR_ID.strip()
        # Convert "10:00 AM" to 24hr for ISO
        t_dt = datetime.datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %I:%M %p")
        
        start_iso = t_dt.strftime(f"%Y-%m-%dT%H:%M:%S{config.UTC_OFFSET}")
        end_iso = (t_dt + timedelta(hours=1)).strftime(f"%Y-%m-%dT%H:%M:%S{config.UTC_OFFSET}")

        # Construct Title & Meet Link
        meet_link = ""
        if summary_template == "TOUR":
            event_summary = f"Tour: {name} will come to visit"
        else:
            event_summary = f"{summary_template}: {name}"
            # Only Manager Meetings get a Google Meet link
            meet_link = config.STATIC_MEET_LINK

        event = {
            'summary': event_summary,
            'description': f"Client: {name}\nEmail: {email}\nNote: Auto-booked via AI Concierge.",
            'start': {'dateTime': start_iso, 'timeZone': config.TIMEZONE},
            'end': {'dateTime': end_iso, 'timeZone': config.TIMEZONE},
        }
        
        # Add location if link exists
        if meet_link:
            event['location'] = meet_link

        try:
            created_event = service.events().insert(
                calendarId=cal_id, 
                body=event
            ).execute()
        except Exception as e:
            print(f"  !! Booking Error: {e}")
            return {"status": "error", "message": f"I couldn't create the event: {str(e)}"}

        # TRIGGER EMAIL NOTIFICATION
        # Fix: Use actual booking type and link, not hardcoded "Tour"
        notifications.send_booking_email(
            client_email=email,
            client_name=name,
            booking_type=summary_template, 
            date=date_str,
            time=time_str,
            meet_link=meet_link
        )
        
        meet_info = f" Your Google Meet link is: {meet_link}" if meet_link else ""
        
        return {
            "status": "success", 
            "message": f"Excellent. I have formally scheduled your {summary_template} for {date_str} at {time_str}. We look forward to it."
        }
    except Exception as e:
        print(f"  !! Booking Error: {e}")
        return {"status": "error", "message": f"I couldn't create the event: {str(e)}"}

def book_tour(name: str, email: str, date_str: str, time_str: str):
    """Schedules a physical tour. Title: 'Tour: [Name] will come to visit'."""
    print(f"\n[TOOL] Booking Tour: {name} | {date_str} at {time_str}")
    return _create_event(name, email, date_str, time_str, "TOUR")

def book_manager_meeting(name: str, email: str, date_str: str, time_str: str):
    """Schedules a virtual meeting. Title: 'Manager Meeting: [Name]'."""
    print(f"\n[TOOL] Booking Meeting: {name} | {date_str} at {time_str}")
    return _create_event(name, email, date_str, time_str, "Manager Meeting")

def search_venue_knowledge(query: str):
    """Searches the venue's knowledge base (PDF) for specific details on pricing, rules, or history."""
    import rag
    return rag.search_knowledge(query)

def get_cal_me():
    """Diagnostic tool to verify access to Google Calendar."""
    print("\n[GOOGLE CAL] Diagnostic Check...")
    service = _get_calendar_service()
    if not service:
        print("  !! Service Not Configured (missing credentials.json)")
        return {}
    
    try:
        # Check overall access
        cal_list = service.calendarList().list().execute()
        entries = cal_list.get('items', [])
        print(f"  <- SUCCESS: Service account has access to {len(entries)} calendars.")
        for entry in entries:
            print(f"     - {entry.get('summary')} (ID: {entry.get('id')})")
        
        # Check specific ID from config
        cal_id = config.GOOGLE_CALENDAR_ID.strip()
        cal = service.calendars().get(calendarId=cal_id).execute()
        print(f"  <- SPECIFIC ID CHECK: Connected to '{cal.get('summary')}'")
        
        # Check Conference Properties
        conf_props = cal.get('conferenceProperties', {})
        solutions = conf_props.get('allowedConferenceSolutionTypes', [])
        print(f"  <- SUPPORTED MEET SOLUTIONS: {solutions}")
        return cal
    except Exception as e:
        print(f"  !! Diagnostic Error: {e}")
        return {}
if __name__ == "__main__":
    get_cal_me()
