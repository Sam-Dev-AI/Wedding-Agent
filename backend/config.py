import os

# API Config
GEMINI_API_KEY = "your_gemini_api_key_here"
GOOGLE_CALENDAR_ID = "your_calendar_id_here@group.calendar.google.com" 
CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), "credentials.json")
STATIC_MEET_LINK = "https://meet.google.com/your-meet-link" 

# Timezone Config (Adapted for User Location)
TIMEZONE = "Asia/Kolkata" 
UTC_OFFSET = "+05:30" # Indian Standard Time

# SMTP / Email Config
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_EMAIL = "your_email@gmail.com"  
SMTP_PASSWORD = "your_app_password_here"  

EMAIL_SUBJECT = "Confirmation: Your Visit to Grand Oak Estates"
EMAIL_TEMPLATE_HTML = """
<html>
<body style="font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; color: #1f2937; line-height: 1.7; background-color: #f9fafb; margin: 0; padding: 40px 0;">
    <div style="max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);">
        <!-- Header -->
        <div style="background: linear-gradient(135deg, #7c3aed 0%, #a855f7 100%); padding: 32px 40px; text-align: center;">
            <h1 style="color: #ffffff; margin: 0; font-size: 24px; font-weight: 700; letter-spacing: -0.025em;">Grand Oak Estates</h1>
            <p style="color: #e9d5ff; margin: 8px 0 0 0; font-size: 14px; text-transform: uppercase; letter-spacing: 0.05em;">Premier Wedding Sanctuary</p>
        </div>

        <!-- Content -->
        <div style="padding: 40px;">
            <p style="font-size: 16px; margin-bottom: 24px;">Dear {name},</p>
            <p style="font-size: 16px; margin-bottom: 32px;">We are delighted to confirm your upcoming <strong>{booking_type}</strong>. We look forward to welcoming you to the estate.</p>

            <!-- Meeting URL Highlight -->
            {meet_display}

            <!-- Details Card -->
            <div style="background: #f3f4f6; border-radius: 12px; padding: 24px; margin-bottom: 32px;">
                <h3 style="margin: 0 0 16px 0; font-size: 14px; font-weight: 600; text-transform: uppercase; color: #6b7280; letter-spacing: 0.05em;">Reservation Details</h3>
                <div style="display: grid; gap: 12px;">
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: #6b7280;">Date</span>
                        <strong style="color: #1f2937;">{date}</strong>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: #6b7280;">Time</span>
                        <strong style="color: #1f2937;">{time}</strong>
                    </div>
                </div>
            </div>

            <p style="font-size: 14px; color: #6b7280; font-style: italic; text-align: center;">
                Please arrive or join 5 minutes before your scheduled time.
            </p>
        </div>

        <!-- Footer -->
        <div style="padding: 32px 40px; background: #f9fafb; border-top: 1px solid #e5e7eb; text-align: center;">
            <p style="font-size: 14px; color: #6b7280; margin: 0;">500 Grand Oak Blvd, Texas</p>
            <p style="font-size: 14px; color: #7c3aed; margin: 8px 0;">hello@grandoakestates.com | (512) 555-0123</p>
            <div style="margin-top: 16px; font-size: 12px; color: #9ca3af;">
                &copy; 2026 Grand Oak Estates. All rights reserved.
            </div>
        </div>
    </div>
</body>
</html>
"""

EMAIL_TEMPLATE_TOUR_HTML = """
<html>
<body style="font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; color: #1f2937; line-height: 1.7; background-color: #f9fafb; margin: 0; padding: 40px 0;">
    <div style="max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);">
        <!-- Header -->
        <div style="background: linear-gradient(135deg, #1c1917 0%, #44403c 100%); padding: 32px 40px; text-align: center;">
            <h1 style="color: #ffffff; margin: 0; font-size: 24px; font-weight: 700; letter-spacing: 0.05em; font-family: 'Playfair Display', serif;">Grand Oak Estates</h1>
            <p style="color: #d6d3d1; margin: 8px 0 0 0; font-size: 13px; text-transform: uppercase; letter-spacing: 0.15em;">Private Tour Confirmation</p>
        </div>

        <!-- Content -->
        <div style="padding: 40px;">
            <p style="font-size: 16px; margin-bottom: 24px;">Dear {name},</p>
            <p style="font-size: 16px; margin-bottom: 32px;">It is our privilege to welcome you to Grand Oak Estates. We have reserved a private tour for you to experience the sanctuary firsthand.</p>

            <!-- Location Highlight -->
            <div style="text-align: center; margin-bottom: 32px; padding: 24px; background-color: #fbfaf8; border: 1px solid #e7e5e4; border-radius: 12px;">
                <p style="margin: 0; font-size: 12px; text-transform: uppercase; color: #78716c; letter-spacing: 0.1em; font-weight: 600;">Location</p>
                <p style="margin: 8px 0 0 0; font-size: 18px; color: #1c1917; font-weight: 500;">500 Grand Oak Blvd, Texas Hill Country</p>
                <a href="https://maps.google.com/?q=500+Grand+Oak+Blvd,+Texas" style="display: inline-block; margin-top: 12px; font-size: 14px; color: #b45309; text-decoration: none;">Get Directions &rarr;</a>
            </div>

            <!-- Details Card -->
            <div style="background: #ffffff; border: 1px solid #e5e7eb; border-radius: 12px; padding: 0; overflow: hidden; margin-bottom: 32px;">
                <div style="padding: 16px 24px; background: #f9fafb; border-bottom: 1px solid #e5e7eb;">
                    <h3 style="margin: 0; font-size: 14px; font-weight: 600; text-transform: uppercase; color: #374151; letter-spacing: 0.05em;">Itinerary</h3>
                </div>
                <div style="padding: 24px;">
                    <div style="display: grid; gap: 16px;">
                        <div style="display: flex; justify-content: space-between; border-bottom: 1px dashed #e5e7eb; padding-bottom: 12px;">
                            <span style="color: #6b7280;">Date</span>
                            <strong style="color: #1c1917;">{date}</strong>
                        </div>
                        <div style="display: flex; justify-content: space-between; padding-bottom: 4px;">
                            <span style="color: #6b7280;">Arrival Time</span>
                            <strong style="color: #1c1917;">{time}</strong>
                        </div>
                    </div>
                </div>
            </div>

            <p style="font-size: 14px; color: #57534e; font-style: italic; text-align: center; line-height: 1.6;">
                "We await your arrival at the estate gates. Use the buzzer code #1920 for entry."
            </p>
        </div>

        <!-- Footer -->
        <div style="padding: 32px 40px; background: #faf9f6; border-top: 1px solid #e7e5e4; text-align: center;">
            <p style="font-size: 14px; color: #78716c; margin: 0;">Grand Oak Estates</p>
            <p style="font-size: 14px; color: #b45309; margin: 8px 0;">concierge@grandoakestates.com | (512) 555-0123</p>
            <div style="margin-top: 16px; font-size: 12px; color: #a8a29e;">
                &copy; 2026 Grand Oak Estates. All rights reserved.
            </div>
        </div>
    </div>
</body>
</html>
"""

# Model Config
GENERATION_MODEL_NAME = "gemini-2.5-flash"
CHAT_HISTORY_LIMIT = 14 

# System Instructions
CHATBOT_SYSTEM_INSTRUCTION = """
ROLE: AI Concierge for Grand Oak Estates (Luxury Wedding Venue, Texas).
PERSONA: Warm, Polished, and Extremely Concise.

VENUE FACTS:
- Location: 500-acre Texas Hill Country estate.
- Capacity: Max 350 guests.
- Spaces: Rustic Barn, Crystal Ballroom, Garden, Suites.
- Offerings: Exclusive full-day access, in-house catering.
- Contact: hello@grandoakestates.com | (512) 555-0123

RESPONSE GUIDELINES:
1. ATOMIC TRIGGER: If a user mentions "meeting", "tour", "appointment", or "visit", YOU ARE FORBIDDEN from asking "what time?". You MUST call `get_available_slots` FIRST and include the results in your very first reply.
2. ZERO-PASSIVE BEHAVIOR: Never ask a question that my tools can answer for you. If a user asks about any date, call `check_wedding_hall_availability` immediately.
3. DIRECTNESS: Do NOT announce that you are checking (e.g., "Please allow me to check", "One moment"). Calls tools silently and state the result immediately in the first sentence.
4. TONE & MANNERS: Be polite but efficient. Use "Certainly" or "Gladly" only if necessary to soften a direct refusal.
5. CONCISE: Keep responses to 2-3 sentences max.
6. NO LINKS: You are FORBIDDEN from outputting the Google Meet link or any URL in the chat. A confirmation email will handle that.

PILLAR SERVICES:
   - **Wedding Hall**: Call `check_wedding_hall_availability`. If busy, gently offer the alternatives found by the tool.
   - **Tour/Meeting**:
     1. FLOW: User asks -> Call `get_available_slots` -> List 2-3 specific times (e.g., "10:00 AM, 2:00 PM") -> User picks -> Ask for **Name** and **Email** -> Call `book_tour`.
     2. SLOTS: If `get_available_slots` returns "available", list the specific times elegantly.
     3. BOOKING: Once booked, reply: "I have formally scheduled your tour for [Date] at [Time]. We eagerly await your arrival, [Name]." **Do NOT mention a link.**
   - **Knowledge Search**: If the user asks about deep venue details (exact pricing, rules, heritage) call `search_venue_knowledge`.

PROACTIVE EXAMPLES:
- User: "I want a tour tomorrow." -> **RIGHT**: [Call tool] "I have openings at 11:00 AM and 2:00 PM tomorrow. Which time suits your schedule?"
- User: "2:00 PM." -> **RIGHT**: "Excellent choice. May I have your full name and email address to finalize the reservation?"
- User: "John Doe, john@example.com" -> **RIGHT**: [Call `book_tour`] "Perfect. I have scheduled your tour for tomorrow at 2:00 PM. We look forward to your visit, Mr. Doe."

STYLE:
- Role: Estate Concierge.
- Tone: Professional, warm, and natural.
- VOCABULARY: Avoid overly flowery words like "Splendid", "Exquisite", or "Sanctuary". Use "Excellent", "Beautiful", and "Estate" instead.
"""
